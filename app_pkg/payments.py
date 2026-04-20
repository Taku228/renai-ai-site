import json
import os
from typing import Dict

from .config import PAYMENTS_DB_PATH


def load_payments_db() -> Dict[str, dict]:
    if not os.path.exists(PAYMENTS_DB_PATH):
        return {}
    with open(PAYMENTS_DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_paid_plan_from_email(email: str) -> str:
    if not email:
        return "無料"
    db = load_payments_db()
    record = db.get(email.strip().lower())
    if not record:
        return "無料"
    if record.get("status") != "active":
        return "無料"
    return record.get("plan", "無料")
