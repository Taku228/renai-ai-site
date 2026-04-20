import html
import re
import streamlit as st
import streamlit.components.v1 as components


def parse_result_text(text: str):
    summary = ""
    advice = ""
    replies = []
    reply_intents = []
    judgement = {"interest_score": "", "safety_score": "", "push_pull": "", "temperature": ""}

    summary_match = re.search(r"【一言】\s*(.*?)\s*【判断】", text, re.DOTALL)
    if not summary_match:
        summary_match = re.search(r"【一言】\s*(.*?)\s*【返信案】", text, re.DOTALL)
    if summary_match:
        summary = summary_match.group(1).strip()

    judgement_block_match = re.search(r"【判断】\s*(.*?)\s*【返信案】", text, re.DOTALL)
    if judgement_block_match:
        for line in [x.strip() for x in judgement_block_match.group(1).strip().splitlines() if x.strip()]:
            if "脈あり度" in line:
                judgement["interest_score"] = re.sub(r"^[-・]?\s*", "", line)
            elif "安全度" in line:
                judgement["safety_score"] = re.sub(r"^[-・]?\s*", "", line)
            elif "押す" in line or "引く" in line or "今は" in line:
                judgement["push_pull"] = re.sub(r"^[-・]?\s*", "", line)
            elif "温度感" in line:
                judgement["temperature"] = re.sub(r"^[-・]?\s*", "", line)

    advice_match = re.search(r"【アドバイス】\s*(.*)", text, re.DOTALL)
    if advice_match:
        advice = advice_match.group(1).strip()

    replies_block_match = re.search(r"【返信案】\s*(.*?)\s*【アドバイス】", text, re.DOTALL)
    if replies_block_match:
        lines = [line.strip() for line in replies_block_match.group(1).strip().splitlines() if line.strip()]
        current_intent = ""
        for line in lines:
            intent_match = re.match(r"^(?:\d+[.)]|[①-③]|\-|\*)?\s*狙い[:：]\s*(.+)$", line)
            if intent_match:
                current_intent = intent_match.group(1).strip()
                continue
            if re.search(r"狙い[:：]", line):
                continue
            reply_match = re.match(r"^(?:\d+[.)]|[①-③]|\-|\*)\s*(.+)$", line)
            if reply_match:
                cleaned = re.sub(r"^返信案\d*[:：]?\s*", "", reply_match.group(1).strip()).strip()
                cleaned = re.sub(r"^（[^）]+）\s*", "", cleaned).strip()
                if re.search(r"^狙い[:：]", cleaned):
                    continue
                if cleaned and len(cleaned) >= 6:
                    replies.append(cleaned)
                    reply_intents.append(current_intent if current_intent else "")
                    current_intent = ""
        if len(replies) == 0:
            for line in lines:
                if re.search(r"狙い[:：]", line):
                    continue
                cleaned = re.sub(r"^返信案\d*[:：]?\s*", "", line).strip()
                cleaned = re.sub(r"^（[^）]+）\s*", "", cleaned).strip()
                if re.search(r"^狙い[:：]", cleaned):
                    continue
                if cleaned and len(cleaned) >= 8:
                    replies.append(cleaned)
                    reply_intents.append("")
                    if len(replies) >= 3:
                        break

    return summary, replies[:3], reply_intents[:3], advice, judgement


def build_full_copy_text(replies, advice):
    if not replies:
        return ""
    lines = [f"{idx}. {reply}" for idx, reply in enumerate(replies, start=1)]
    if advice:
        lines += ["", "アドバイス:", advice]
    return "\n".join(lines)


def copy_button_component(text: str, label: str, key_suffix: str):
    safe_text = html.escape(text)
    safe_label = html.escape(label)
    components.html(
        f"""
        <div style="margin: 0.15rem 0 0.25rem 0;">
            <textarea id="copy_text_{key_suffix}" style="position:absolute; left:-9999px; top:-9999px;">{safe_text}</textarea>
            <button onclick="const text = document.getElementById('copy_text_{key_suffix}').value; navigator.clipboard.writeText(text).then(() => {{ const msg = document.getElementById('copy_msg_{key_suffix}'); msg.innerText = 'コピーしました'; setTimeout(() => msg.innerText = '', 1400); }}).catch(() => {{ const msg = document.getElementById('copy_msg_{key_suffix}'); msg.innerText = 'コピーに失敗しました'; setTimeout(() => msg.innerText = '', 1400); }});" style="width:100%; background:#2563eb; color:white; border:none; padding:0.72rem 0.95rem; border-radius:0.7rem; cursor:pointer; font-size:0.98rem; font-weight:700;">{safe_label}</button>
            <div id="copy_msg_{key_suffix}" style="margin-top:6px; color:#16a34a; font-size:0.9rem; font-weight:600;"></div>
        </div>
        """,
        height=88,
    )


def show_reply_card(index: int, reply: str, intent: str):
    st.markdown(
        f"""
        <div class="reply-card">
            <div class="badge">返信案 {index}</div>
            <div style="font-size:1rem; line-height:1.8; color:#0f172a; word-break:break-word;">{html.escape(reply)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if intent:
        st.markdown(f"<div class='reply-meta'>狙い：{html.escape(intent)}</div>", unsafe_allow_html=True)
    copy_button_component(reply, f"{index}番をコピー", f"reply_{index}")
