import time
import streamlit as st
from openai import OpenAI

from app_pkg.config import (
    PAGE_TITLE, PAGE_ICON, LAYOUT, PLAN_CONFIG,
    MAX_USER_MESSAGE_LEN, MAX_CONTEXT_LEN, MIN_INTERVAL_SECONDS,
    SYSTEM_PROMPT, env_settings,
)
from app_pkg.styles import APP_CSS
from app_pkg.state import init_state, reset_form
from app_pkg.logic import (
    contains_block_words, build_template_text, get_model_name,
    get_light_memory_context, get_standard_memory_context,
    save_history, get_upgrade_message, should_lock_continuous_judgement,
    next_wait_seconds, get_effective_plan,
)
from app_pkg.parsing import parse_result_text, build_full_copy_text, show_reply_card, copy_button_component
from app_pkg.ui import (
    render_header, render_law_page, render_paywall,
    render_standard_upgrade_box, render_judgement,
    render_free_lock, render_footer_links,
)
from app_pkg.payments import resolve_paid_plan_from_email

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)
settings = env_settings()
client = OpenAI(api_key=settings["api_key"]) if settings["api_key"] else None

query_params = st.query_params
page_mode = query_params.get("page", "app")
if page_mode == "law":
    render_law_page()
    st.stop()

st.markdown(APP_CSS, unsafe_allow_html=True)
render_header()
init_state()

# 購入確認
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("### 購入済みの方")
customer_email = st.text_input(
    "購入時のメールアドレス",
    value=st.session_state.get("customer_email", ""),
    placeholder="例: yourmail@example.com",
)
st.session_state.customer_email = customer_email
if st.button("購入状態を確認する", use_container_width=True):
    st.session_state.paid_plan = resolve_paid_plan_from_email(customer_email)
    st.rerun()
if st.session_state.paid_plan != "無料":
    st.success(f"購入確認済みです。現在の有効プラン: {st.session_state.paid_plan}")
else:
    st.markdown("<div class='small-note'>未購入の場合は無料プランとして利用されます。</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Plan section
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("### プラン")
selected_plan = st.selectbox("プランを選択してください", ["無料", "ライト", "スタンダード"], index=["無料", "ライト", "スタンダード"].index(st.session_state.plan))
if selected_plan != st.session_state.plan:
    st.session_state.plan = selected_plan
    st.session_state.usage_count = 0
    st.session_state.daily_total_count = 0
    st.session_state.last_memory_preview = ""
    st.session_state.show_paywall = False
    st.rerun()

effective_plan = get_effective_plan(st.session_state.plan, st.session_state.paid_plan)
plan_cfg = PLAN_CONFIG[effective_plan]
session_limit = plan_cfg["session_limit"]
daily_limit = plan_cfg["daily_limit"]

st.markdown("""
<div class="plan-card"><div class="plan-title">無料</div><div class="small-note">単発で試したい人向け。<br>会話の記憶なし。</div></div>
<div class="plan-card"><div class="plan-title">ライト <span style="font-size:0.85rem;color:#475569;">月額580円</span></div><div class="small-note">直前の流れを踏まえて相談したい人向け。<br>『さっきこれ送ったけど次どうする？』に強い。</div></div>
<div class="plan-card-highlight"><div class="plan-title">スタンダード ★おすすめ <span style="font-size:0.85rem;color:#475569;">月額980円</span></div><div class="small-note">同じ相手との流れを記憶。<br>毎回説明しなくてよくなる、本命向けプラン。</div></div>
""", unsafe_allow_html=True)
st.markdown(f"<div class='small-note'>選択中のプラン: <b>{st.session_state.plan}</b><br>現在利用できるプラン: <b>{effective_plan}</b><br>料金目安: {PLAN_CONFIG[st.session_state.plan]['price_text']}<br>記憶機能: {PLAN_CONFIG[st.session_state.plan]['memory_mode']}<br>{PLAN_CONFIG[st.session_state.plan]['memory_sales']}</div>", unsafe_allow_html=True)

if st.session_state.plan in ["ライト", "スタンダード"] and effective_plan == "無料":
    st.markdown("""
    <div class="upgrade-box">
        <b>このプランは購入後に使えます</b><br>
        現在は無料プランとして利用中です。<br>
        下の購入ボタンからお申し込み後、購入時のメールアドレスで購入状態を確認してください。
    </div>
    """, unsafe_allow_html=True)
    if st.session_state.plan == "ライト" and settings["stripe_light_url"]:
        st.link_button("ライトプランを購入する", settings["stripe_light_url"], use_container_width=True)
    if st.session_state.plan == "スタンダード" and settings["stripe_standard_url"]:
        st.link_button("スタンダードプランを購入する", settings["stripe_standard_url"], use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

remaining_session = max(session_limit - st.session_state.usage_count, 0)
remaining_daily = max(daily_limit - st.session_state.daily_total_count, 0)
st.info(f"現在利用中のプラン: {effective_plan} / このセッション残り: {remaining_session} 回 / 今日の全体残り: {remaining_daily} 回")
if st.session_state.usage_count >= session_limit:
    st.warning("このプランでのセッション利用回数を使い切りました。")
    st.markdown(f"<div class='upgrade-box'><b>アップグレードのメリット</b><br>{get_upgrade_message(effective_plan)}</div>", unsafe_allow_html=True)
    st.stop()
if st.session_state.daily_total_count >= daily_limit:
    st.warning("今日の利用上限に達しました。")
    st.markdown(f"<div class='upgrade-box'><b>もっと相談したい場合</b><br>{get_upgrade_message(effective_plan)}</div>", unsafe_allow_html=True)
    st.stop()

# Input section
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("### 入力")
st.markdown("<div class='small-note'>相手のメッセージと状況を入れてください</div>", unsafe_allow_html=True)
st.info("👇 まずは相手のメッセージだけ入れて試してみてください")
partner_name = ""
if plan_cfg["allow_partner_name"]:
    partner_name = st.text_input("相手の名前（ニックネーム）", placeholder="例：さやか、アプリの人A")
    st.markdown("<div class='small-note'>このプランでは相手ごとに流れを分けて相談できます。</div>", unsafe_allow_html=True)

relationship = st.selectbox("相手との関係性", ["友達", "気になる人", "付き合う前", "マッチングアプリで知り合った相手"], key="relationship")
tone = st.selectbox("返信の雰囲気", ["自然", "やさしめ", "ちょい軽め", "丁寧", "距離を少し縮めたい"], key="tone")
goal = st.selectbox("今回どうしたいですか？", ["自然に返したい", "好印象を残したい", "少し距離を縮めたい", "次の約束につなげたい"], key="goal")
situation_template = st.selectbox("状況テンプレ", ["なし", "初デート後", "まだ距離がある", "脈ありか不安", "返信が遅い相手", "マッチングアプリ"], key="situation_template")
st.markdown(f"<div class='small-note'>記憶状態: {plan_cfg['memory_message']}</div>", unsafe_allow_html=True)
user_message = st.text_area("相手から来たメッセージ", height=160, placeholder="例：今日はありがとう！すごく楽しかったね！", key="user_message")
extra_context = st.text_area("補足（任意）", height=110, placeholder="例：昨日初デートでした。相手は少し控えめな感じです。", key="extra_context")

template_text = build_template_text(situation_template)
if template_text:
    st.markdown(f"<div class='small-note'>状況テンプレ適用中: {template_text}</div>", unsafe_allow_html=True)

memory_context_preview = ""
if effective_plan == "ライト":
    memory_context_preview = get_light_memory_context()
elif effective_plan == "スタンダード":
    memory_context_preview = get_standard_memory_context(partner_name)
st.session_state.last_memory_preview = memory_context_preview

if memory_context_preview:
    st.markdown('<div class="memory-box">', unsafe_allow_html=True)
    st.markdown("**今回の返信で考慮される記憶**")
    st.markdown("<div class='small-note'>この内容を踏まえて、続きとして返信案を作ります。</div>", unsafe_allow_html=True)
    st.text_area("memory_preview", value=memory_context_preview, height=180, disabled=True, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
elif effective_plan == "無料":
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

if generate_button:
    if not settings["api_key"] or client is None:
        st.error("OPENAI_API_KEY が設定されていません。")
        st.stop()
    elapsed = time.time() - st.session_state.last_request_time
    if elapsed < MIN_INTERVAL_SECONDS:
        st.warning(f"連続利用防止のため、あと {next_wait_seconds(st.session_state.last_request_time, MIN_INTERVAL_SECONDS)} 秒待ってください。")
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
    if effective_plan == "スタンダード" and not partner_name.strip():
        st.warning("スタンダードでは相手名（ニックネーム）を入力してください。")
        st.stop()

    with st.spinner("返信案を考えています..."):
        combined_context = extra_context.strip()
        if template_text:
            combined_context = f"{template_text}\n{combined_context}" if combined_context else template_text
        memory_context = ""
        if effective_plan == "ライト":
            memory_context = get_light_memory_context()
        elif effective_plan == "スタンダード":
            memory_context = get_standard_memory_context(partner_name.strip())
        prompt = f"""
現在のプラン: {effective_plan}
記憶モード: {plan_cfg['memory_mode']}
相手名: {partner_name.strip() if partner_name.strip() else '未設定'}
相手との関係性: {relationship}
希望する口調: {tone}
今回の目的: {goal}

過去の記憶情報:
{memory_context if memory_context else 'なし'}

相手から来たメッセージ:
{user_message}

補足情報:
{combined_context if combined_context else 'なし'}
"""
        prompt += "\nこの返信は実際に送る前提で、自然さを最優先してください。"
        prompt += "\n不自然な表現やテンプレ感は絶対に避けてください。"
        prompt += "\n相手の温度感を判断して、その温度感に合った自然な返信を作ってください。"
        prompt += "\n無理に距離を縮めず、実際に送って違和感のない文面を優先してください。"
        prompt += "\n返信案はそのままコピペして使える完成文にしてください。"
        prompt += "\nラベル（無難・やさしめ・少し攻め等）は書かないでください。"
        prompt += "\n返信案は必ず3つ、改行区切りで、各案に文章を含めて出力してください。"
        prompt += "\n返信案は必ず次の形式で出してください。\n1. 返信文\n2. 返信文\n3. 返信文"
        prompt += "\n箇条書き記号（①、-、*）は使わないでください。"
        prompt += "\n判断結果は、ユーザーがすぐ理解できる短い表現で出してください。"
        prompt += "\n『狙い：...』は必ず返信文とは別の行にしてください。返信文の先頭に『狙い：』を入れないでください。"
        if effective_plan == "無料" and not st.session_state.is_first_time:
            prompt += "\n無料プランでは判断パートは省略してください。無料プランでは各返信案の『狙い』も省略してください。無料プランでは返信案3つと短いアドバイスだけを出してください。"
        else:
            prompt += "\n判断パートも含めて出力してください。各返信案ごとに『狙い』も短く付けてください。"
        if st.session_state.usage_count == 0:
            prompt += "\n初回なので特に自然で実用的な返信を優先してください。"

        response = client.responses.create(
            model=get_model_name(effective_plan),
            max_output_tokens=320 if (effective_plan == "無料" and st.session_state.is_first_time) else (220 if effective_plan == "無料" else 360),
            input=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
        )
        summary_text, parsed_replies, reply_intents, advice_text, judgement = parse_result_text(response.output_text)
        st.session_state.result_text = response.output_text
        st.session_state.parsed_replies = parsed_replies
        st.session_state.reply_intents = reply_intents
        st.session_state.advice_text = advice_text
        st.session_state.summary_text = summary_text
        st.session_state.judgement = judgement
        st.session_state.usage_count += 1
        st.session_state.daily_total_count += 1
        st.session_state.last_request_time = time.time()
        if st.session_state.is_first_time:
            st.session_state.is_first_time = False
        save_history(effective_plan, partner_name.strip(), user_message.strip(), combined_context, parsed_replies, advice_text)

# Results
if st.session_state.result_text:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="result-title">結果</div>', unsafe_allow_html=True)
    if effective_plan == "ライト":
        st.markdown("""<div class="memory-box"><b>ライトの記憶を使っています</b><br>直前の相談の流れを踏まえて、次の返信案を作っています。</div>""", unsafe_allow_html=True)
    elif effective_plan == "スタンダード":
        st.markdown("""<div class="memory-box"><b>スタンダードの記憶を使っています</b><br>同じ相手との過去の流れを踏まえて、続きとして返信案を作っています。</div>""", unsafe_allow_html=True)
    if st.session_state.summary_text:
        st.success(st.session_state.summary_text)

    if should_lock_continuous_judgement(effective_plan):
        render_standard_upgrade_box(settings["stripe_standard_url"])
    elif effective_plan != "無料" or st.session_state.is_first_time:
        if any(st.session_state.judgement.values()):
            render_judgement(st.session_state.judgement)
    elif effective_plan == "無料" and not st.session_state.is_first_time:
        render_free_lock()
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
    if not replies:
        st.warning("返信案の解析に失敗しました。下の『AIの元の出力を表示』をご確認ください。")
    if replies:
        st.markdown("### 返信案")
        for idx, reply in enumerate(replies, start=1):
            intent = st.session_state.reply_intents[idx - 1] if idx - 1 < len(st.session_state.reply_intents) else ""
            show_reply_card(idx, reply, intent)

    if st.session_state.advice_text:
        st.markdown('<hr class="soft">', unsafe_allow_html=True)
        st.markdown("### アドバイス")
        st.write(st.session_state.advice_text)

    st.markdown('<hr class="soft">', unsafe_allow_html=True)
    st.markdown("### まとめてコピー")
    full_copy_text = build_full_copy_text(replies, st.session_state.advice_text)
    st.code(full_copy_text, language=None)
    copy_button_component(full_copy_text, "まとめてコピー", "full_copy")
    st.markdown("<div class='copy-help'>スマホでもそのまま貼り付けやすい形です。</div>", unsafe_allow_html=True)

    st.markdown("### 次の相談につなげる")
    if effective_plan == "無料":
        st.markdown("<div class='small-note'>この返信を送った後の続きも相談できますが、前回の流れは自動では引き継がれません。</div>", unsafe_allow_html=True)
    elif effective_plan == "ライト":
        st.markdown("<div class='small-note'>この返信の続きも相談できます。さらに相手との流れを踏まえた深い判断は、スタンダードで使えます。</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='small-note'>同じ相手名で続ければ、この相手との流れを踏まえて相談できます。</div>", unsafe_allow_html=True)

    if effective_plan == "無料":
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

    if effective_plan == "無料" and st.session_state.usage_count >= 1:
        st.markdown("""
        <div class="upgrade-box">
            <b>前回の流れも踏まえて相談したいですか？</b><br>
            ライト以上なら、直前のやり取りを考慮して次の返信を提案できます。
        </div>
        """, unsafe_allow_html=True)

    if effective_plan == "無料" and st.session_state.get("show_paywall"):
        render_paywall(settings["stripe_light_url"], settings["stripe_standard_url"])

    if effective_plan != "スタンダード":
        st.markdown(f"<div class='upgrade-box'><b>もっと続き相談をしやすくするには</b><br>{get_upgrade_message(effective_plan)}</div>", unsafe_allow_html=True)

    with st.expander("AIの元の出力を表示"):
        st.text_area("全文", value=st.session_state.result_text, height=260, key="raw_result_text")

    remaining_session = max(session_limit - st.session_state.usage_count, 0)
    remaining_daily = max(daily_limit - st.session_state.daily_total_count, 0)
    st.info(f"現在利用中のプラン: {effective_plan} / このセッション残り: {remaining_session} 回 / 今日の全体残り: {remaining_daily} 回")
    st.markdown("</div>", unsafe_allow_html=True)

render_footer_links()
