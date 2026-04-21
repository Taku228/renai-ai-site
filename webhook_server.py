import json
import os
from flask import Flask, request, jsonify
import stripe

app = Flask(__name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
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


@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.get("/payment-status")
def payment_status():
    email = request.args.get("email", "").strip().lower()
    if not email:
        return jsonify({"ok": False, "error": "email is required"}), 400

    db = load_db()
    record = db.get(email, {"plan": "無料", "status": "none"})
    return jsonify({
        "ok": True,
        "email": email,
        "record": record,
    })


@app.post("/stripe-webhook")
def stripe_webhook():
    try:
        payload = request.data
        sig_header = request.headers.get("Stripe-Signature", "")

        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=webhook_secret,
        )

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            customer_email = (
                (session.get("customer_details", {}) or {}).get("email")
                or session.get("customer_email")
            )

            plan_name = "無料"

            try:
                line_items = stripe.checkout.Session.list_line_items(session["id"], limit=10)
                for item in line_items.data:
                    price_id = item["price"]["id"]
                    if price_id in PRICE_TO_PLAN:
                        plan_name = PRICE_TO_PLAN[price_id]
                        break
            except Exception as e:
                print("line_items error:", repr(e))

            if customer_email and plan_name != "無料":
                db = load_db()
                key = customer_email.strip().lower()
                db[key] = {
                    "plan": plan_name,
                    "status": "active",
                }
                save_db(db)
                print("saved payment:", key, db[key])

        return jsonify({"ok": True})

    except Exception as e:
        print("webhook error:", repr(e))
        return jsonify({"ok": False, "error": repr(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))