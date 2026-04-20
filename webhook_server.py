import json
import os
from flask import Flask, request, jsonify
import stripe

app = Flask(__name__)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
db_path = os.getenv("PAYMENTS_DB_PATH", "payments_db.json")

PRICE_TO_PLAN = {
    os.getenv("STRIPE_LIGHT_PRICE_ID", ""): "ライト",
    os.getenv("STRIPE_STANDARD_PRICE_ID", ""): "スタンダード",
}


def load_db():
    if not os.path.exists(db_path):
        return {}
    with open(db_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(db):
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


@app.post("/stripe-webhook")
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        event = stripe.Webhook.construct_event(payload=payload, sig_header=sig_header, secret=webhook_secret)
    except Exception:
        return jsonify({"ok": False}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = (session.get("customer_details", {}) or {}).get("email") or session.get("customer_email")
        line_items = stripe.checkout.Session.list_line_items(session["id"], limit=10)
        plan_name = "無料"
        for item in line_items.data:
            price_id = item["price"]["id"]
            if price_id in PRICE_TO_PLAN:
                plan_name = PRICE_TO_PLAN[price_id]
                break
        if customer_email and plan_name != "無料":
            db = load_db()
            db[customer_email.strip().lower()] = {"plan": plan_name, "status": "active"}
            save_db(db)

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
        if customer_id:
            customer = stripe.Customer.retrieve(customer_id)
            email = customer.get("email")
            if email:
                db = load_db()
                key = email.strip().lower()
                if key in db:
                    db[key]["status"] = "canceled"
                    save_db(db)

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
