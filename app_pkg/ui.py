import html
import streamlit as st


def render_header() -> None:
    st.markdown(
        """
        <div class="main-card">
            <div class="app-title">💬 やさしい恋愛相談AI</div>
            <div class="app-subtitle">LINE返信に悩む男性向けの、やさしい相談役AIです。</div>
            <div class="small-note">相手のメッセージを入れるだけで、自然な返信案を3つ提案します。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_law_page() -> None:
    st.title("特定商取引法に基づく表記")
    fields = [
        ("販売事業者", "小倉　拓人"),
        ("運営責任者", "小倉　拓人"),
        ("所在地", "日本国内（詳細住所は請求があった場合、遅滞なく開示いたします）"),
        ("メールアドレス", "taku.child.0228@gmail.com"),
        ("販売価格", "ライトプラン：月額580円（税込）\nスタンダードプラン：月額980円（税込）"),
        ("商品代金以外の必要料金", "インターネット接続料金、通信料金等はお客様のご負担となります。"),
        ("支払方法", "クレジットカード決済（Stripe）"),
        ("支払時期", "サブスクリプション申込時に決済され、その後は契約内容に応じて毎月自動更新されます。"),
        ("サービス提供時期", "決済完了後、直ちに利用可能です。"),
        ("返品・キャンセルについて", "デジタルサービスの性質上、購入後の返品・返金には原則として応じられません。\n解約は次回更新日前までに所定の方法で行うことで、翌月以降の請求を停止できます。"),
        ("動作環境", "インターネット接続可能なスマートフォンまたはPCの最新ブラウザ環境"),
    ]
    for title, body in fields:
        st.subheader(title)
        for line in body.split("\n"):
            st.write(line)
    st.link_button("↩️ アプリに戻る", "./")


def render_paywall(stripe_light_url: str, stripe_standard_url: str) -> None:
    st.markdown(
        """
        <div class="paywall-box">
            <div style="font-size:1.05rem; font-weight:800; margin-bottom:0.4rem;">🔒 続きは有料機能です</div>
            <div style="line-height:1.8;">
                有料プランでは、返信を作るだけでなく<br>
                「この返信を送って大丈夫か」を判断できます。<br><br>
                ・安全度の評価<br>
                ・脈あり度の見立て<br>
                ・押すべきか / 少し待つべきか<br>
                ・次の一手の提案
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### ライトプラン（月額580円）")
    st.markdown("<div class='small-note'>送信前の判断を見ながら、失敗しにくく進めたい人向けです。</div>", unsafe_allow_html=True)
    if stripe_light_url:
        st.link_button("ライトプランを開始する", stripe_light_url, use_container_width=True)
    st.markdown("### スタンダードプラン（月額980円）")
    st.markdown("<div class='small-note'>同じ相手との流れまで踏まえて、本気で相談したい人向けです。</div>", unsafe_allow_html=True)
    if stripe_standard_url:
        st.link_button("スタンダードを開始する", stripe_standard_url, use_container_width=True)


def render_standard_upgrade_box(stripe_standard_url: str) -> None:
    st.markdown(
        """
        <div class="upgrade-box">
            <div style="font-size:1.02rem; font-weight:800; margin-bottom:0.45rem;">🔒 この先の「流れを踏まえた判断」はスタンダード向きです</div>
            <div style="line-height:1.8;">
                今回の相談は、前回までの流れを踏まえて判断するほど価値が上がります。<br><br>
                スタンダードでは、<br>
                ・脈あり度の変化<br>
                ・関係の進み方<br>
                ・今は押すべきか待つべきか<br>
                ・次の一手<br>
                を、同じ相手との流れを踏まえて確認できます。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div class='small-note' style='margin-bottom:0.7rem;'>単発の返信提案ではなく、『この相手との流れで今どう動くべきか』を見たい人向けです。</div>", unsafe_allow_html=True)
    if stripe_standard_url:
        st.link_button("スタンダードにアップグレードする", stripe_standard_url, use_container_width=True)


def render_judgement(judgement: dict) -> None:
    st.markdown("<div class='judgement-box'><div style='font-weight:800; margin-bottom:0.55rem;'>判断結果</div>", unsafe_allow_html=True)
    if judgement.get("safety_score"):
        st.markdown(f"<div class='meter-row'><b>安全度：</b>{html.escape(judgement['safety_score'])}</div>", unsafe_allow_html=True)
    if judgement.get("interest_score"):
        st.markdown(f"<div class='meter-row'><b>脈あり度：</b>{html.escape(judgement['interest_score'])}</div>", unsafe_allow_html=True)
    if judgement.get("push_pull"):
        st.markdown(f"<div class='meter-row'><b>おすすめ行動：</b>{html.escape(judgement['push_pull'])}</div>", unsafe_allow_html=True)
    if judgement.get("temperature"):
        st.markdown(f"<div class='meter-row'><b>相手の温度感：</b>{html.escape(judgement['temperature'])}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_free_lock() -> None:
    st.markdown(
        """
        <div class="judgement-box">
            <div style="font-weight:800; margin-bottom:0.45rem;">🔒 この返信、送って大丈夫？</div>
            <div style="line-height:1.8;">
                このまま送って問題ないかを、AIが判断します。<br><br>
                ・嫌われるリスク<br>
                ・脈あり度<br>
                ・押すべきか、少し待つべきか<br>
                ・次の一手<br><br>
                続きは有料プランで確認できます。
            </div>
        </div>
        <div class="small-note" style="margin-bottom:0.6rem;">返信を作るだけでなく、「送って大丈夫か」を確認したい人向けです。</div>
        """,
        unsafe_allow_html=True,
    )


def render_footer_links() -> None:
    st.markdown("""
    <hr class="soft">
    <div style="text-align:center; font-size:0.9rem; line-height:1.9;">
        <a href="?page=law">特定商取引法に基づく表記</a>
    </div>
    """, unsafe_allow_html=True)
