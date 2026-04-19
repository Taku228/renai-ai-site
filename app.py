import os
import re
import time
import html
from datetime import date

import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

# ----------------------------
# 基本設定
# ----------------------------
st.set_page_config(
    page_title="やさしい恋愛相談AI",
    page_icon="💬",
    layout="centered"
)

# ----------------------------
# 特商法ページ切替
# ----------------------------
query_params = st.query_params
page_mode = query_params.get("page", "app")


def render_tokutei_page():
    st.title("特定商取引法に基づく表記")

    st.subheader("販売事業者")
    st.write("あなたの氏名または事業者名")

    st.subheader("運営責任者")
    st.write("あなたの氏名")

    st.subheader("所在地")
    st.write("請求があった場合、遅滞なく開示します。")

    st.subheader("メールアドレス")
    st.write("yourmail@example.com")

    st.subheader("販売価格")
    st.write("ライトプラン：月額580円（税込）")
    st.write("スタンダードプラン：月額980円（税込）")

    st.subheader("商品代金以外の必要料金")
    st.write("インターネット接続料金、通信料金等はお客様のご負担となります。")

    st.subheader("支払方法")
    st.write("クレジットカード決済（Stripe）")

    st.subheader("支払時期")
    st.write("サブスクリプション申込時に決済され、その後は契約内容に応じて毎月自動更新されます。")

    st.subheader("サービス提供時期")
    st.write("決済完了後、直ちに利用可能です。")

    st.subheader("返品・キャンセルについて")
    st.write("デジタルサービスの性質上、購入後の返品・返金には原則として応じられません。")
    st.write("解約は次回更新日前までに所定の方法で行うことで、翌月以降の請求を停止できます。")

    st.subheader("動作環境")
    st.write("インターネット接続可能なスマートフォンまたはPCの最新ブラウザ環境")

    st.link_button("↩️ アプリに戻る", "./")


if page_mode == "law":
    render_tokutei_page()
    st.stop()

# ----------------------------
# CSS
# ----------------------------
st.markdown("""
<style>

/* ===== レイアウト（最重要） ===== */
.block-container {
    padding-top: 6.5rem;
    padding-bottom: 2rem;
    max-width: 860px;
}

@media (max-width: 640px) {
    .block-container {
        padding-top: 8.2rem;
        padding-left: 0.7rem;
        padding-right: 0.7rem;
        padding-bottom: 1.5rem;
    }
}

/* ===== カード共通 ===== */
.main-card,
.section-card,
.reply-card,
.plan-card,
.plan-card-highlight,
.memory-box,
.upgrade-box,
.judgement-box,
.paywall-box {
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 1rem;
    line-height: 1.7;
    color: #0f172a !important;
}

.main-card *,
.section-card *,
.reply-card *,
.plan-card *,
.plan-card-highlight *,
.memory-box *,
.upgrade-box *,
.judgement-box *,
.paywall-box * {
    color: #0f172a !important;
}

/* ===== カード個別 ===== */
.main-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
}

.section-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
}

.reply-card {
    background: #ffffff;
    border: 1px solid #dbeafe;
}

.plan-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
}

.plan-card-highlight {
    background: #eff6ff;
    border: 1px solid #3b82f6;
}

.memory-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
}

/* ===== 課金導線 ===== */
.upgrade-box {
    background: #fff7ed;
    border: 1px solid #fb923c;
    color: #7c2d12 !important;
}

.upgrade-box * {
    color: #7c2d12 !important;
}

/* ===== 判定ボックス ===== */
.judgement-box {
    background: #ecfeff;
    border: 1px solid #67e8f9;
}

/* ===== ペイウォール ===== */
.paywall-box {
    background: #fef3c7;
    border: 1px solid #f59e0b;
}

/* ===== テキスト ===== */
.app-title {
    font-size: 1.72rem;
    font-weight: 800;
    margin-bottom: 0.18rem;
    line-height: 1.3;
}

.app-subtitle {
    color: #475569 !important;
    font-size: 0.98rem;
    line-height: 1.6;
    margin-bottom: 0.18rem;
}

.result-title {
    font-size: 1.16rem;
    font-weight: 800;
    margin-bottom: 0.6rem;
}

.plan-title {
    font-size: 1rem;
    font-weight: 800;
    margin-bottom: 0.35rem;
}

.small-note,
.reply-meta,
.copy-help {
    color: #475569 !important;
    font-size: 0.95rem;
}

.badge {
    display: inline-block;
    font-size: 0.85rem;
    font-weight: 700;
    padding: 0.25rem 0.55rem;
    border-radius: 999px;
    background: #eff6ff;
    color: #1d4ed8 !important;
    border: 1px solid #bfdbfe;
    margin-bottom: 0.55rem;
}

.meter-row {
    margin: 0.25rem 0;
}

hr.soft {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 0.95rem 0 0.8rem 0;
}

/* ===== ボタン ===== */
.stButton > button {
    border-radius: 12px;
    padding: 0.6rem 1rem;
    font-weight: 700;
    min-height: 48px;
    font-size: 0.98rem;
}

div[data-testid="stTextArea"] textarea {
    border-radius: 12px;
    font-size: 16px !important;
    line-height: 1.6;
}

div[data-testid="stSelectbox"] > div {
    border-radius: 12px;
}

/* ===== スマホ微調整 ===== */
@media (max-width: 640px) {
    .main-card,
    .section-card,
    .reply-card,
    .plan-card,
    .plan-card-highlight,
    .memory-box,
    .upgrade-box,
    .judgement-box,
    .paywall-box {
        padding: 0.9rem;
        font-size: 0.95rem;
    }

    .app-title {
        font-size: 1.35rem;
    }

    .app-subtitle {
        font-size: 0.93rem;
    }

    .result-title {
        font-size: 1.05rem;
    }

    .small-note {
        font-size: 0.9rem;
    }

    .stButton > button {
        min-height: 50px;
        font-size: 1rem;
    }
}

/* ===== Streamlit余計な表示 ===== */
header, footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------
# ヘッダー
# ----------------------------
st.markdown("""
<div class="main-card">
    <div class="app-title">💬 やさしい恋愛相談AI</div>
    <div class="app-subtitle">
        LINE返信に悩む男性向けの、やさしい相談役AIです。
    </div>
    <div class="small-note">
        相手のメッセージを入れるだけで、自然な返信案を3つ提案します。
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# 環境変数
# ----------------------------
api_key = os.getenv("OPENAI_API_KEY")
access_code = os.getenv("APP_ACCESS_CODE")
stripe_light_url = os.getenv("STRIPE_LIGHT_URL", "")
stripe_standard_url = os.getenv("STRIPE_STANDARD_URL", "")

if not api_key:
    st.error("OPENAI_API_KEY が設定されていません。")
    st.stop()

if not access_code:
    st.error("APP_ACCESS_CODE が設定されていません。")
    st.stop()

client = OpenAI(api_key=api_key)

# ----------------------------
# セッション状態初期化
# ----------------------------
defaults = {
    "is_unlocked": False,
    "usage_count": 0,
    "last_request_time": 0.0,
    "daily_date": str(date.today()),
    "daily_total_count": 0,
    "relationship": "友達",
    "tone": "自然",
    "goal": "自然に返したい",
    "situation_template": "なし",
    "user_message": "",
    "extra_context": "",
    "result_text": "",
    "parsed_replies": [],
    "reply_intents": [],
    "advice_text": "",
    "summary_text": "",
    "plan": "無料",
    "chat_history": [],
    "partner_histories": {},
    "last_memory_preview": "",
    "show_paywall": False,
    "judgement": {
        "interest_score": "",
        "safety_score": "",
        "push_pull": "",
        "temperature": ""
    },
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

today_str = str(date.today())
if st.session_state.daily_date != today_str:
    st.session_state.daily_date = today_str
    st.session_state.daily_total_count = 0

# ----------------------------
# プラン設定
# ----------------------------
PLAN_CONFIG = {
    "無料": {
        "session_limit": 3,
        "daily_limit": 10,
        "memory_mode": "記憶なし",
        "memory_message": "その場で1回ずつ相談できます。",
        "memory_sales": "まずはお試し用。毎回シンプルに相談したい人向け。",
        "allow_partner_name": False,
        "price_text": "0円",
    },
    "ライト": {
        "session_limit": 8,
        "daily_limit": 30,
        "memory_mode": "直前の流れを記憶",
        "memory_message": "直前の相談履歴を最大3件ぶん考慮して返信します。",
        "memory_sales": "『さっきこれを送ったんだけど次どうする？』に強いプランです。",
        "allow_partner_name": False,
        "price_text": "月額580円想定",
    },
    "スタンダード": {
        "session_limit": 20,
        "daily_limit": 100,
        "memory_mode": "相手ごとに記憶",
        "memory_message": "相手名ごとに相談履歴を分けて、続きから相談できます。",
        "memory_sales": "毎回説明しなくてよくなる、本命向けの継続相談プランです。",
        "allow_partner_name": True,
        "price_text": "月額980円想定",
    },
}

PAID_PLANS = ["ライト", "スタンダード"]

BLOCK_WORDS = [
    "system prompt",
    "ignore previous instructions",
    "developer message",
    "jailbreak",
    "プロンプトを表示",
    "内部指示",
    "ルールを無視",
]

MAX_USER_MESSAGE_LEN = 180
MAX_CONTEXT_LEN = 160
MIN_INTERVAL_SECONDS = 8

current_plan = st.session_state.plan
plan_cfg = PLAN_CONFIG[current_plan]
FREE_LIMIT_PER_SESSION = plan_cfg["session_limit"]
DAILY_LIMIT_ALL = plan_cfg["daily_limit"]

# ----------------------------
# 補助関数
# ----------------------------
def contains_block_words(text: str) -> bool:
    lower = text.lower()
    return any(word.lower() in lower for word in BLOCK_WORDS)


def reset_form():
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
        "temperature": ""
    }


def build_template_text(template_name: str) -> str:
    templates = {
        "なし": "",
        "初デート後": "昨日は初デートのあとです。相手に重くならず、自然に好印象を残したいです。",
        "まだ距離がある": "相手とはまだ少し距離があります。馴れ馴れしすぎず、自然にやり取りを続けたいです。",
        "脈ありか不安": "相手が自分に興味を持っているか少し不安です。慎重すぎず、でも押しすぎない返信にしたいです。",
        "返信が遅い相手": "相手は返信が遅めです。プレッシャーを与えず、感じよく返したいです。",
        "マッチングアプリ": "マッチングアプリで知り合った相手です。軽すぎず重すぎず、会話が続きやすい返信にしたいです。",
    }
    return templates.get(template_name, "")


def parse_result_text(text: str):
    summary = ""
    advice = ""
    replies = []
    reply_intents = []
    judgement = {
        "interest_score": "",
        "safety_score": "",
        "push_pull": "",
        "temperature": ""
    }

    summary_match = re.search(r"【一言】\s*(.*?)\s*【判断】", text, re.DOTALL)
    if not summary_match:
        summary_match = re.search(r"【一言】\s*(.*?)\s*【返信案】", text, re.DOTALL)
    if summary_match:
        summary = summary_match.group(1).strip()

    judgement_block_match = re.search(r"【判断】\s*(.*?)\s*【返信案】", text, re.DOTALL)
    if judgement_block_match:
        judgement_block = judgement_block_match.group(1).strip()
        for line in [x.strip() for x in judgement_block.splitlines() if x.strip()]:
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
        replies_block = replies_block_match.group(1).strip()
        lines = [line.strip() for line in replies_block.splitlines() if line.strip()]

        current_intent = ""
        for line in lines:
            intent_match = re.match(r"^\d+\.\s*狙い[:：]\s*(.+)$", line)
            if intent_match:
                current_intent = intent_match.group(1).strip()
                continue

            reply_match = re.match(r"^\d+\.\s*(.+)$", line)
            if reply_match:
                cleaned = reply_match.group(1).strip()
                cleaned = re.sub(r"^（[^）]+）\s*", "", cleaned).strip()
                if cleaned and len(cleaned) >= 6:
                    replies.append(cleaned)
                    reply_intents.append(current_intent if current_intent else "")
                    current_intent = ""

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
            <button
                onclick="
                    const text = document.getElementById('copy_text_{key_suffix}').value;
                    navigator.clipboard.writeText(text).then(() => {{
                        const msg = document.getElementById('copy_msg_{key_suffix}');
                        msg.innerText = 'コピーしました';
                        setTimeout(() => msg.innerText = '', 1400);
                    }}).catch(() => {{
                        const msg = document.getElementById('copy_msg_{key_suffix}');
                        msg.innerText = 'コピーに失敗しました';
                        setTimeout(() => msg.innerText = '', 1400);
                    }});
                "
                style="
                    width:100%;
                    background:#2563eb;
                    color:white;
                    border:none;
                    padding:0.72rem 0.95rem;
                    border-radius:0.7rem;
                    cursor:pointer;
                    font-size:0.98rem;
                    font-weight:700;
                "
            >
                {safe_label}
            </button>
            <div id="copy_msg_{key_suffix}" style="margin-top:6px; color:#16a34a; font-size:0.9rem; font-weight:600;"></div>
        </div>
        """,
        height=88,
    )


def show_reply_card(index: int, reply: str, intent: str):
    st.markdown(f"""
    <div class="reply-card">
        <div class="badge">返信案 {index}</div>
        <div style="font-size:1rem; line-height:1.8; color:#0f172a; word-break:break-word;">{html.escape(reply)}</div>
    </div>
    """, unsafe_allow_html=True)
    if intent:
        st.markdown(f"<div class='reply-meta'>狙い：{html.escape(intent)}</div>", unsafe_allow_html=True)
    copy_button_component(reply, f"{index}番をコピー", f"reply_{index}")


def get_light_memory_context():
    history = st.session_state.chat_history[-3:]
    if not history:
        return ""

    lines = []
    for i, item in enumerate(history, start=1):
        lines.append(f"[直近相談 {i}]")
        lines.append(f"相手メッセージ: {item.get('user_message', '')}")
        lines.append(f"補足: {item.get('extra_context', 'なし')}")
        lines.append(f"前回おすすめ返信: {item.get('best_reply', '')}")
        lines.append(f"前回アドバイス: {item.get('advice_text', '')}")
        lines.append("")
    return "\n".join(lines).strip()


def get_standard_memory_context(partner_name: str):
    if not partner_name:
        return ""

    partner_history = st.session_state.partner_histories.get(partner_name, [])
    history = partner_history[-5:]
    if not history:
        return ""

    lines = [f"相手名: {partner_name}"]
    for i, item in enumerate(history, start=1):
        lines.append(f"[過去履歴 {i}]")
        lines.append(f"相手メッセージ: {item.get('user_message', '')}")
        lines.append(f"補足: {item.get('extra_context', 'なし')}")
        lines.append(f"前回おすすめ返信: {item.get('best_reply', '')}")
        lines.append(f"前回アドバイス: {item.get('advice_text', '')}")
        lines.append("")
    return "\n".join(lines).strip()


def save_history(plan_name: str, partner_name: str, user_message: str, extra_context: str, replies: list, advice_text: str):
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

    elif plan_name == "スタンダード":
        if partner_name:
            if partner_name not in st.session_state.partner_histories:
                st.session_state.partner_histories[partner_name] = []
            st.session_state.partner_histories[partner_name].append(record)
            st.session_state.partner_histories[partner_name] = st.session_state.partner_histories[partner_name][-5:]


def get_upgrade_message(plan_name: str):
    if plan_name == "無料":
        return "続きから相談したいなら、ライト以上で『流れを踏まえた返信』が使えます。"
    if plan_name == "ライト":
        return "同じ相手との流れをしっかり管理したいなら、スタンダードが向いています。"
    return "今のプランでは相手ごとの流れまで扱えます。"


def get_model_name(plan_name: str) -> str:
    if plan_name == "無料":
        return "gpt-4.1-mini"
    return "gpt-4.1"


def render_paywall():
    st.markdown("""
    <div class="paywall-box">
        <div style="font-size:1.05rem; font-weight:800; margin-bottom:0.4rem;">
            🔒 この先は有料機能です
        </div>
        <div style="line-height:1.8;">
            この返信について、さらに次の内容を確認できます。<br>
            ・この返信の安全度<br>
            ・脈あり度の見立て<br>
            ・今は押すべきか引くべきか<br>
            ・次の一手の提案
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ライトプラン（月額580円想定）")
    st.markdown("<div class='small-note'>返信の続き相談や、送信前の判断支援を使いたい人向けです。</div>", unsafe_allow_html=True)
    if stripe_light_url:
        st.link_button("ライトプランを開始する", stripe_light_url, use_container_width=True)
    else:
        st.info("Stripeリンクを設定すると、ここから購入できるようになります。")

    st.markdown("### スタンダードプラン（月額980円想定）")
    st.markdown("<div class='small-note'>相手ごとの流れを踏まえて、より深く相談したい人向けです。</div>", unsafe_allow_html=True)
    if stripe_standard_url:
        st.link_button("スタンダードを開始する", stripe_standard_url, use_container_width=True)
    else:
        st.info("Stripeリンクを設定すると、ここから購入できるようになります。")


# ----------------------------
# 合言葉チェック
# ----------------------------
if not st.session_state.is_unlocked:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 利用コードを入力してください")
    code_input = st.text_input("アクセスコード", type="password")

    if st.button("利用を開始する", use_container_width=True):
        if code_input == access_code:
            st.session_state.is_unlocked = True
            st.success("認証できました。使えます。")
            st.rerun()
        else:
            st.error("アクセスコードが違います。")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ----------------------------
# プランUI
# ----------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("### プラン")

selected_plan = st.selectbox(
    "プランを選択してください",
    ["無料", "ライト", "スタンダード"],
    index=["無料", "ライト", "スタンダード"].index(st.session_state.plan)
)

if selected_plan != st.session_state.plan:
    st.session_state.plan = selected_plan
    st.session_state.usage_count = 0
    st.session_state.daily_total_count = 0
    st.session_state.last_memory_preview = ""
    st.session_state.show_paywall = False
    st.rerun()

plan_cfg = PLAN_CONFIG[st.session_state.plan]
FREE_LIMIT_PER_SESSION = plan_cfg["session_limit"]
DAILY_LIMIT_ALL = plan_cfg["daily_limit"]

if st.session_state.plan in PAID_PLANS:
    st.warning("このプランは現在テスト中です。")
    unlock_code = st.text_input("有料プラン用コードを入力", type="password")
    if unlock_code != "vip123":
        st.markdown("""
        <div class="small-note">
            テスト中のため、有料プラン用コードが必要です。
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

st.markdown("""
<div class="plan-card">
    <div class="plan-title">無料</div>
    <div class="small-note">
        単発で試したい人向け。<br>
        会話の記憶なし。
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="plan-card">
    <div class="plan-title">ライト <span style="font-size:0.85rem;color:#475569;">月額580円想定</span></div>
    <div class="small-note">
        直前の流れを踏まえて相談したい人向け。<br>
        「さっきこれ送ったけど次どうする？」に強い。
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="plan-card-highlight">
    <div class="plan-title">スタンダード ★おすすめ <span style="font-size:0.85rem;color:#475569;">月額980円想定</span></div>
    <div class="small-note">
        同じ相手との流れを記憶。<br>
        毎回説明しなくてよくなる、本命向けプラン。
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="small-note">
現在のプラン: <b>{st.session_state.plan}</b><br>
料金目安: {plan_cfg["price_text"]}<br>
記憶機能: {plan_cfg["memory_mode"]}<br>
{plan_cfg["memory_sales"]}
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# 回数制限表示
# ----------------------------
remaining_session = max(FREE_LIMIT_PER_SESSION - st.session_state.usage_count, 0)
remaining_daily = max(DAILY_LIMIT_ALL - st.session_state.daily_total_count, 0)

st.info(f"現在のプラン: {st.session_state.plan} / このセッション残り: {remaining_session} 回 / 今日の全体残り: {remaining_daily} 回")

if st.session_state.usage_count >= FREE_LIMIT_PER_SESSION:
    st.warning("このプランでのセッション利用回数を使い切りました。")
    st.markdown(f"""
    <div class="upgrade-box">
        <b>アップグレードのメリット</b><br>
        {get_upgrade_message(st.session_state.plan)}
    </div>
    """, unsafe_allow_html=True)
    st.button("アップグレードを検討する", use_container_width=True)
    st.stop()

if st.session_state.daily_total_count >= DAILY_LIMIT_ALL:
    st.warning("今日の利用上限に達しました。")
    st.markdown(f"""
    <div class="upgrade-box">
        <b>もっと相談したい場合</b><br>
        {get_upgrade_message(st.session_state.plan)}
    </div>
    """, unsafe_allow_html=True)
    st.button("有料プランを見る", use_container_width=True)
    st.stop()

# ----------------------------
# 入力UI
# ----------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("### 入力")
st.markdown("<div class='small-note'>相手のメッセージと状況を入れてください</div>", unsafe_allow_html=True)
st.info("👇 まずは相手のメッセージだけ入れて試してみてください")

if plan_cfg["allow_partner_name"]:
    partner_name = st.text_input("相手の名前（ニックネーム）", placeholder="例：さやか、アプリの人A")
    st.markdown("<div class='small-note'>このプランでは相手ごとに流れを分けて相談できます。</div>", unsafe_allow_html=True)
else:
    partner_name = ""

relationship = st.selectbox(
    "相手との関係性",
    ["友達", "気になる人", "付き合う前", "マッチングアプリで知り合った相手"],
    key="relationship"
)

tone = st.selectbox(
    "返信の雰囲気",
    ["自然", "やさしめ", "ちょい軽め", "丁寧", "距離を少し縮めたい"],
    key="tone"
)

goal = st.selectbox(
    "今回どうしたいですか？",
    ["自然に返したい", "好印象を残したい", "少し距離を縮めたい", "次の約束につなげたい"],
    key="goal"
)

situation_template = st.selectbox(
    "状況テンプレ",
    ["なし", "初デート後", "まだ距離がある", "脈ありか不安", "返信が遅い相手", "マッチングアプリ"],
    key="situation_template"
)

st.markdown(f"<div class='small-note'>記憶状態: {plan_cfg['memory_message']}</div>", unsafe_allow_html=True)

user_message = st.text_area(
    "相手から来たメッセージ",
    height=160,
    placeholder="例：今日はありがとう！すごく楽しかったね！",
    key="user_message"
)

extra_context = st.text_area(
    "補足（任意）",
    height=110,
    placeholder="例：昨日初デートでした。相手は少し控えめな感じです。",
    key="extra_context"
)

template_text = build_template_text(situation_template)
if template_text:
    st.markdown(f"<div class='small-note'>状況テンプレ適用中: {template_text}</div>", unsafe_allow_html=True)

memory_context_preview = ""
if st.session_state.plan == "ライト":
    memory_context_preview = get_light_memory_context()
elif st.session_state.plan == "スタンダード":
    memory_context_preview = get_standard_memory_context(partner_name)

st.session_state.last_memory_preview = memory_context_preview

if memory_context_preview:
    st.markdown('<div class="memory-box">', unsafe_allow_html=True)
    st.markdown("**今回の返信で考慮される記憶**")
    st.markdown("<div class='small-note'>この内容を踏まえて、続きとして返信案を作ります。</div>", unsafe_allow_html=True)
    st.text_area(
        "memory_preview",
        value=memory_context_preview,
        height=180,
        disabled=True,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
elif st.session_state.plan == "無料":
    st.markdown("<div class='small-note'>無料プランでは、前回までの流れは引き継がれません。</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.markdown(f"<div class='small-note'>相手メッセージ: {len(user_message)}/{MAX_USER_MESSAGE_LEN} 文字</div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='small-note'>補足: {len(extra_context)}/{MAX_CONTEXT_LEN} 文字</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    generate_button = st.button("返信案を作る", use_container_width=True)
with col2:
    st.button("入力をリセット", use_container_width=True, on_click=reset_form)

st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# プロンプト
# ----------------------------
system_prompt = """
あなたは恋愛経験が豊富で、LINEのやり取りが上手い男性の相談役です。
ユーザーは20代男性で、恋愛経験が少なく、実際に送る返信に悩んでいます。

あなたの役割は「そのまま送っても自然でうまくいきやすい返信」を作ることに加え、
今この返信を送って大丈夫かどうかを判断し、失敗しにくい方向へ導くことです。

▼重要ルール（最優先）
- 必ず「実際に送る前提」で書く
- 不自然・キザ・テンプレ感のある文章は禁止
- 相手との距離感を絶対に崩さない
- 男性が無理なく送れる文にする

▼精度を上げるために必ずやること
- 相手のメッセージの意図を一度考える
- 温度感（そっけない / 普通 / 好意あり気味）を内部で判断する
- 押すべきか引くべきかを判断する
- ユーザーの目的と相手の温度感がズレる場合は、無理に攻めすぎない

▼判断パートについて
- 脈あり度は 0〜100% で出す
- 安全度は ★1〜5 で出す
- 押す / 引く / 様子見 のどれが良いか短く出す
- 温度感も短く出す
- すべて短く、わかりやすく書く
- 断定しすぎない

▼返信案の作り方（かなり重要）
- 3つとも必ずキャラを変える
- 1つ目は最も無難で自然
- 2つ目はやさしくて好印象
- 3つ目は少しだけ距離を縮める
- ただし、出力にはラベルを書かない
- 3つともそのままコピペして使える完成文にする
- 3つとも必ず文章を含める
- 1行に1案ずつ出す
- 各返信案ごとに「狙い」を1行で短く付ける

▼NG例
- 同じような文章を3つ
- 丁寧すぎて会話にならない
- わざとらしい優しさ
- モテテクっぽすぎる文章
- ラベルだけの出力

▼理想
「これなら普通に送る」「ちょっといい感じになるかも」「今は攻めすぎない方がいい」が直感でわかること

▼アドバイスについて
- 短くていい
- 実際の行動に役立つ内容だけ書く

▼出力形式
有料プランでは以下の形式:

【一言】
（短く共感）

【判断】
・脈あり度：...
・安全度：...
・今は：...
・温度感：...

【返信案】
1. 狙い：...
1. ...
2. 狙い：...
2. ...
3. 狙い：...
3. ...

【アドバイス】
...

無料プランでは以下の形式:

【一言】
（短く共感）

【返信案】
1. ...
2. ...
3. ...

【アドバイス】
...
"""

# ----------------------------
# 生成処理
# ----------------------------
if generate_button:
    now = time.time()
    elapsed = now - st.session_state.last_request_time

    if elapsed < MIN_INTERVAL_SECONDS:
        wait_sec = int(MIN_INTERVAL_SECONDS - elapsed) + 1
        st.warning(f"連続利用防止のため、あと {wait_sec} 秒待ってください。")
        st.stop()

    if not user_message.strip():
        st.warning("相手から来たメッセージを入力してください。")
        st.stop()

    if len(user_message) > MAX_USER_MESSAGE_LEN:
        st.warning(f"相手から来たメッセージは {MAX_USER_MESSAGE_LEN} 文字以内にしてください。")
        st.stop()

    if len(extra_context) > MAX_CONTEXT_LEN:
        st.warning(f"補足は {MAX_CONTEXT_LEN} 文字以内にしてください。")
        st.stop()

    if contains_block_words(user_message) or contains_block_words(extra_context):
        st.warning("その入力内容では利用できません。")
        st.stop()

    if st.session_state.plan == "スタンダード" and not partner_name.strip():
        st.warning("スタンダードでは相手名（ニックネーム）を入力してください。")
        st.stop()

    with st.spinner("返信案を考えています..."):
        try:
            combined_context = extra_context.strip()
            if template_text:
                combined_context = f"{template_text}\n{combined_context}" if combined_context else template_text

            memory_context = ""
            if st.session_state.plan == "ライト":
                memory_context = get_light_memory_context()
            elif st.session_state.plan == "スタンダード":
                memory_context = get_standard_memory_context(partner_name.strip())

            prompt = f"""
現在のプラン: {st.session_state.plan}
記憶モード: {plan_cfg["memory_mode"]}
相手名: {partner_name.strip() if partner_name.strip() else "未設定"}
相手との関係性: {relationship}
希望する口調: {tone}
今回の目的: {goal}

過去の記憶情報:
{memory_context if memory_context else "なし"}

相手から来たメッセージ:
{user_message}

補足情報:
{combined_context if combined_context else "なし"}
"""
            prompt += "\nこの返信は実際に送る前提で、自然さを最優先してください。"
            prompt += "\n不自然な表現やテンプレ感は絶対に避けてください。"
            prompt += "\n相手の温度感を判断して、その温度感に合った自然な返信を作ってください。"
            prompt += "\n無理に距離を縮めず、実際に送って違和感のない文面を優先してください。"
            prompt += "\n返信案はそのままコピペして使える完成文にしてください。"
            prompt += "\nラベル（無難・やさしめ・少し攻め等）は書かないでください。"
            prompt += "\n返信案は必ず3つ、改行区切りで、各案に文章を含めて出力してください。"

            if st.session_state.plan == "無料":
                prompt += "\n無料プランでは判断パートは省略してください。"
                prompt += "\n無料プランでは各返信案の『狙い』も省略してください。"
                prompt += "\n無料プランでは返信案3つと短いアドバイスだけを出してください。"
            else:
                prompt += "\n判断パートも含めて出力してください。"
                prompt += "\n各返信案ごとに『狙い』も短く付けてください。"

            if st.session_state.usage_count == 0:
                prompt += "\n初回なので特に自然で実用的な返信を優先してください。"

            model_name = get_model_name(st.session_state.plan)

            response = client.responses.create(
                model=model_name,
                max_output_tokens=220 if st.session_state.plan == "無料" else 360,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )

            result_text = response.output_text
            summary_text, parsed_replies, reply_intents, advice_text, judgement = parse_result_text(result_text)

            if len(parsed_replies) < 3:
                parsed_replies = [r for r in parsed_replies if len(r) >= 6]
                reply_intents = reply_intents[:len(parsed_replies)]

            st.session_state.result_text = result_text
            st.session_state.parsed_replies = parsed_replies
            st.session_state.reply_intents = reply_intents
            st.session_state.advice_text = advice_text
            st.session_state.summary_text = summary_text
            st.session_state.judgement = judgement
            st.session_state.usage_count += 1
            st.session_state.daily_total_count += 1
            st.session_state.last_request_time = time.time()

            save_history(
                plan_name=st.session_state.plan,
                partner_name=partner_name.strip(),
                user_message=user_message.strip(),
                extra_context=combined_context,
                replies=parsed_replies,
                advice_text=advice_text
            )

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# ----------------------------
# 結果表示
# ----------------------------
if st.session_state.result_text:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="result-title">結果</div>', unsafe_allow_html=True)

    if st.session_state.plan == "ライト":
        st.markdown("""
        <div class="memory-box">
            <b>ライトの記憶を使っています</b><br>
            直前の相談の流れを踏まえて、次の返信案を作っています。
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.plan == "スタンダード":
        st.markdown("""
        <div class="memory-box">
            <b>スタンダードの記憶を使っています</b><br>
            同じ相手との過去の流れを踏まえて、続きとして返信案を作っています。
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.summary_text:
        st.success(st.session_state.summary_text)

    judgement = st.session_state.judgement

    if st.session_state.plan != "無料" and any(judgement.values()):
        st.markdown("""
        <div class="judgement-box">
            <div style="font-weight:800; margin-bottom:0.45rem;">判断</div>
        """, unsafe_allow_html=True)

        if judgement.get("interest_score"):
            st.markdown(f"<div class='meter-row'>{html.escape(judgement['interest_score'])}</div>", unsafe_allow_html=True)
        if judgement.get("safety_score"):
            st.markdown(f"<div class='meter-row'>{html.escape(judgement['safety_score'])}</div>", unsafe_allow_html=True)
        if judgement.get("push_pull"):
            st.markdown(f"<div class='meter-row'>{html.escape(judgement['push_pull'])}</div>", unsafe_allow_html=True)
        if judgement.get("temperature"):
            st.markdown(f"<div class='meter-row'>{html.escape(judgement['temperature'])}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.plan == "無料":
        st.markdown("""
        <div class="judgement-box">
            <div style="font-weight:800; margin-bottom:0.45rem;">🔒 送る前の判断</div>
            <div style="line-height:1.8;">
                この返信の安全度、脈あり度、押すべきか引くべきかは<br>
                有料プランで確認できます。
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("この返信を評価する（有料）", use_container_width=True):
                st.session_state.show_paywall = True
                st.rerun()
        with col_b:
            if st.button("次の一手を知る（有料）", use_container_width=True):
                st.session_state.show_paywall = True
                st.rerun()

    replies = st.session_state.parsed_replies
    reply_intents = st.session_state.reply_intents
    advice = st.session_state.advice_text

    if replies:
        st.markdown("### 返信案")
        for idx, reply in enumerate(replies, start=1):
            intent = reply_intents[idx - 1] if idx - 1 < len(reply_intents) else ""
            show_reply_card(idx, reply, intent)

    if advice:
        st.markdown('<hr class="soft">', unsafe_allow_html=True)
        st.markdown("### アドバイス")
        st.write(advice)

    st.markdown('<hr class="soft">', unsafe_allow_html=True)
    st.markdown("### まとめてコピー")
    full_copy_text = build_full_copy_text(replies, advice)
    st.code(full_copy_text, language=None)
    copy_button_component(full_copy_text, "まとめてコピー", "full_copy")
    st.markdown("<div class='copy-help'>スマホでもそのまま貼り付けやすい形です。</div>", unsafe_allow_html=True)

    st.markdown("### 次の相談につなげる")
    if st.session_state.plan == "無料":
        st.markdown("<div class='small-note'>この返信を送った後の続きも相談できますが、前回の流れは自動では引き継がれません。</div>", unsafe_allow_html=True)
    elif st.session_state.plan == "ライト":
        st.markdown("<div class='small-note'>この返信を送った後の流れを、そのまま続けて相談できます。</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='small-note'>同じ相手名で続ければ、この相手との流れを踏まえて相談できます。</div>", unsafe_allow_html=True)

    if st.session_state.plan == "無料":
        st.markdown("""
        <div class="upgrade-box">
            <b>この先が有料プラン向きです</b><br>
            ・前回の流れを踏まえた続き相談<br>
            ・同じ相手とのやり取りを記憶<br>
            ・毎回説明しなくても自然な返信提案<br>
            ・送って大丈夫かの判断を見ながら相談<br><br>
            今回の返信の続きを相談したい人は、ライト以上が向いています。
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.plan == "無料" and st.session_state.usage_count >= 1:
        st.markdown("""
        <div class="upgrade-box">
            <b>前回の流れも踏まえて相談したいですか？</b><br>
            ライト以上なら、直前のやり取りを考慮して次の返信を提案できます。
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.plan == "無料" and st.session_state.get("show_paywall"):
        render_paywall()

    if st.session_state.plan != "スタンダード":
        st.markdown(f"""
        <div class="upgrade-box">
            <b>もっと続き相談をしやすくするには</b><br>
            {get_upgrade_message(st.session_state.plan)}
        </div>
        """, unsafe_allow_html=True)

    with st.expander("AIの元の出力を表示"):
        st.text_area(
            "全文",
            value=st.session_state.result_text,
            height=260,
            key="raw_result_text"
        )

    remaining_session = max(FREE_LIMIT_PER_SESSION - st.session_state.usage_count, 0)
    remaining_daily = max(DAILY_LIMIT_ALL - st.session_state.daily_total_count, 0)
    st.info(f"現在のプラン: {st.session_state.plan} / このセッション残り: {remaining_session} 回 / 今日の全体残り: {remaining_daily} 回")
    st.markdown("</div>", unsafe_allow_html=True)