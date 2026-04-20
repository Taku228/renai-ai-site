import time
import streamlit as st
from .config import BLOCK_WORDS, TEMPLATE_TEXTS


def contains_block_words(text: str) -> bool:
    lower = text.lower()
    return any(word.lower() in lower for word in BLOCK_WORDS)


def build_template_text(template_name: str) -> str:
    return TEMPLATE_TEXTS.get(template_name, "")


def get_model_name(plan_name: str) -> str:
    return "gpt-4.1-mini" if plan_name == "無料" else "gpt-4.1"


def get_effective_plan(selected_plan: str, paid_plan: str) -> str:
    if selected_plan == "無料":
        return "無料"
    if paid_plan == selected_plan:
        return selected_plan
    return "無料"


def get_light_memory_context() -> str:
    history = st.session_state.chat_history[-3:]
    if not history:
        return ""
    lines = []
    for i, item in enumerate(history, start=1):
        lines += [
            f"[直近相談 {i}]",
            f"相手メッセージ: {item.get('user_message', '')}",
            f"補足: {item.get('extra_context', 'なし')}",
            f"前回おすすめ返信: {item.get('best_reply', '')}",
            f"前回アドバイス: {item.get('advice_text', '')}",
            "",
        ]
    return "\n".join(lines).strip()


def get_standard_memory_context(partner_name: str) -> str:
    if not partner_name:
        return ""
    partner_history = st.session_state.partner_histories.get(partner_name, [])[-5:]
    if not partner_history:
        return ""
    lines = [f"相手名: {partner_name}"]
    for i, item in enumerate(partner_history, start=1):
        lines += [
            f"[過去履歴 {i}]",
            f"相手メッセージ: {item.get('user_message', '')}",
            f"補足: {item.get('extra_context', 'なし')}",
            f"前回おすすめ返信: {item.get('best_reply', '')}",
            f"前回アドバイス: {item.get('advice_text', '')}",
            "",
        ]
    return "\n".join(lines).strip()


def save_history(plan_name: str, partner_name: str, user_message: str, extra_context: str, replies: list, advice_text: str) -> None:
    best_reply = replies[0] if replies else ""
    record = {
        "user_message": user_message,
        "extra_context": extra_context if extra_context else "なし",
        "best_reply": best_reply,
        "advice_text": advice_text if advice_text else "",
    }
    if plan_name == "ライト":
        st.session_state.chat_history.append(record)
        st.session_state.chat_history = st.session_state.chat_history[-3:]
    elif plan_name == "スタンダード" and partner_name:
        st.session_state.partner_histories.setdefault(partner_name, []).append(record)
        st.session_state.partner_histories[partner_name] = st.session_state.partner_histories[partner_name][-5:]


def get_upgrade_message(plan_name: str) -> str:
    if plan_name == "無料":
        return "続きから相談したいなら、ライト以上で『流れを踏まえた返信』が使えます。"
    if plan_name == "ライト":
        return "同じ相手との流れをしっかり管理したいなら、スタンダードが向いています。"
    return "今のプランでは相手ごとの流れまで扱えます。"


def should_lock_continuous_judgement(plan_name: str) -> bool:
    return plan_name == "ライト" and st.session_state.usage_count >= 1


def next_wait_seconds(last_request_time: float, min_interval_seconds: int) -> int:
    elapsed = time.time() - last_request_time
    return int(min_interval_seconds - elapsed) + 1
