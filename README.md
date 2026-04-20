# やさしい恋愛相談AI

Streamlit で動く恋愛相談AIです。無料 / ライト / スタンダードの導線と、Stripe Payment Link + Webhook による最小の購入判定を含みます。

## 構成

- `app.py`: Streamlit 本体
- `app_pkg/`: UI / ロジック / パース / 支払い判定
- `webhook_server.py`: Stripe Webhook 受信用の小さな Flask サーバー
- `payments_db.json`: 購入者メールとプランを保存する簡易DB（自動生成）

## 使い方

### 1. Streamlit 側

`.streamlit/secrets.toml.example` を参考に `.streamlit/secrets.toml` を作成します。

必要な値:

- `OPENAI_API_KEY`
- `STRIPE_LIGHT_URL`
- `STRIPE_STANDARD_URL`
- `REVIEW_MODE`（通常は `false`）
- `PAYMENTS_DB_PATH`（通常は `payments_db.json`）

起動:

```bash
streamlit run app.py
```

### 2. Webhook 側

必要な環境変数:

- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_LIGHT_PRICE_ID`
- `STRIPE_STANDARD_PRICE_ID`
- `PAYMENTS_DB_PATH`

起動:

```bash
python webhook_server.py
```

### 3. Stripe ダッシュボード

Webhook エンドポイントに以下を登録:

- `checkout.session.completed`
- `customer.subscription.deleted`

Payment Links で使っている Price ID を `STRIPE_LIGHT_PRICE_ID` と `STRIPE_STANDARD_PRICE_ID` に設定してください。

## 運用イメージ

1. ユーザーが Payment Link で購入
2. Stripe が Webhook を送信
3. `payments_db.json` にメール + プランが保存される
4. ユーザーがアプリ上で購入時メールを入力
5. 購入状態を確認すると `paid_plan` が有効化される

## 注意

- この構成は最小構成です。最初の本番には向いていますが、長期的には Supabase / Firebase などのDBに置き換えるのがおすすめです。
- Payment Link と購入確認メールが一致しないと、有料判定できません。
