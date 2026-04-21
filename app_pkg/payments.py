import os
import requests

PAYMENT_STATUS_API_URL = os.getenv("PAYMENT_STATUS_API_URL", "").strip()


def resolve_paid_plan_from_email(email: str) -> str:
    if not email:
        return "無料"

    if not PAYMENT_STATUS_API_URL:
        return "無料"

    try:
        resp = requests.get(
            PAYMENT_STATUS_API_URL,
            params={"email": email.strip().lower()},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        record = data.get("record", {})

        if record.get("status") == "active":
            return record.get("plan", "無料")

        return "無料"
    except Exception as e:
        print("resolve_paid_plan_from_email error:", str(e))
        return "無料"