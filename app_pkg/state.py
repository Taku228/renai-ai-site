from datetime import date
import streamlit as st
from .config import DEFAULTS


def init_state() -> None:
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, dict) else value
    today_str = str(date.today())
    if st.session_state.daily_date != today_str:
        st.session_state.daily_date = today_str
        st.session_state.daily_total_count = 0


def reset_form() -> None:
    st.session_state.relationship = "友達"
    st.session_state.tone = "自然"
    st.session_state.goal = "自然に返したい"
    st.session_state.situation_template = "なし"
    st.session_state.user_message = ""
    st.session_state.extra_context = ""
    st.session_state.result_text = ""
    st.session_state.parsed_replies = []
    st.session_state.reply_intents = []
    st.session_state.advice_text = ""
    st.session_state.summary_text = ""
    st.session_state.last_memory_preview = ""
    st.session_state.show_paywall = False
    st.session_state.judgement = {
        "interest_score": "",
        "safety_score": "",
        "push_pull": "",
        "temperature": "",
    }
