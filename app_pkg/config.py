import os
from datetime import date

PAGE_TITLE = "やさしい恋愛相談AI"
PAGE_ICON = "💬"
LAYOUT = "centered"

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
        "memory_sales": "『さっきこれ送ったけど次どうする？』に強いプランです。",
        "allow_partner_name": False,
        "price_text": "月額580円",
    },
    "スタンダード": {
        "session_limit": 20,
        "daily_limit": 100,
        "memory_mode": "相手ごとに記憶",
        "memory_message": "相手名ごとに相談履歴を分けて、続きから相談できます。",
        "memory_sales": "毎回説明しなくてよくなる、本命向けの継続相談プランです。",
        "allow_partner_name": True,
        "price_text": "月額980円",
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
PAYMENTS_DB_PATH = os.getenv("PAYMENTS_DB_PATH", "payments_db.json")

DEFAULTS = {
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
    "paid_plan": "無料",
    "customer_email": "",
    "chat_history": [],
    "partner_histories": {},
    "last_memory_preview": "",
    "show_paywall": False,
    "is_first_time": True,
    "judgement": {
        "interest_score": "",
        "safety_score": "",
        "push_pull": "",
        "temperature": "",
    },
}

TEMPLATE_TEXTS = {
    "なし": "",
    "初デート後": "昨日は初デートのあとです。相手に重くならず、自然に好印象を残したいです。",
    "まだ距離がある": "相手とはまだ少し距離があります。馴れ馴れしすぎず、自然にやり取りを続けたいです。",
    "脈ありか不安": "相手が自分に興味を持っているか少し不安です。慎重すぎず、でも押しすぎない返信にしたいです。",
    "返信が遅い相手": "相手は返信が遅めです。プレッシャーを与えず、感じよく返したいです。",
    "マッチングアプリ": "マッチングアプリで知り合った相手です。軽すぎず重すぎず、会話が続きやすい返信にしたいです。",
}

SYSTEM_PROMPT = """
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
- 判断には短い理由がにじむように書く
- ユーザーが3秒で理解できる表現にする
- 難しい言い方は避ける

▼返信案の作り方
- 3つとも必ずキャラを変える
- 1つ目は最も無難で自然
- 2つ目はやさしくて好印象
- 3つ目は少しだけ距離を縮める
- ただし、出力にはラベルを書かない
- 3つともそのままコピペして使える完成文にする
- 3つとも必ず文章を含める
- 1行に1案ずつ出す
- 各返信案ごとに「狙い」を1行で短く付ける

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


def env_settings():
    return {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "stripe_light_url": os.getenv("STRIPE_LIGHT_URL", ""),
        "stripe_standard_url": os.getenv("STRIPE_STANDARD_URL", ""),
        "review_mode": os.getenv("REVIEW_MODE", "false").lower() == "true",
    }
