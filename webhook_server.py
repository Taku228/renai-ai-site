@app.post("/stripe-webhook")
def stripe_webhook():
    try:
        payload = request.data
        sig_header = request.headers.get("Stripe-Signature", "")

        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=webhook_secret,
            )
        except Exception as e:
            print("webhook verify error:", repr(e))
            return jsonify({"ok": False, "error": f"verify error: {repr(e)}"}), 400

        print("event type:", event.get("type"))

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            print("session id:", session.get("id"))

            customer_email = (
                (session.get("customer_details", {}) or {}).get("email")
                or session.get("customer_email")
            )
            print("customer_email:", customer_email)

            plan_name = "無料"

            try:
                line_items = stripe.checkout.Session.list_line_items(session["id"], limit=10)
                print("line_items count:", len(line_items.data))
                for item in line_items.data:
                    price_id = item["price"]["id"]
                    print("price_id:", price_id)
                    if price_id in PRICE_TO_PLAN:
                        plan_name = PRICE_TO_PLAN[price_id]
                        break
            except Exception as e:
                print("line_items error:", repr(e))

            print("resolved plan_name:", plan_name)

            if customer_email and plan_name != "無料":
                db = load_db()
                key = customer_email.strip().lower()
                db[key] = {
                    "plan": plan_name,
                    "status": "active",
                }
                save_db(db)
                print("saved payment:", key, db[key])

        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            customer_id = subscription.get("customer")
            print("subscription deleted, customer_id:", customer_id)

            if customer_id:
                try:
                    customer = stripe.Customer.retrieve(customer_id)
                    email = customer.get("email")
                    print("customer email:", email)
                    if email:
                        db = load_db()
                        key = email.strip().lower()
                        if key in db:
                            db[key]["status"] = "canceled"
                            save_db(db)
                            print("canceled payment:", key, db[key])
                except Exception as e:
                    print("subscription delete error:", repr(e))

        return jsonify({"ok": True})

    except Exception as e:
        print("stripe_webhook fatal error:", repr(e))
        return jsonify({"ok": False, "error": repr(e)}), 500