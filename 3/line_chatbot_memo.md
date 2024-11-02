LINE Botとして AWS Lambda + Amazon Bedrock を連携する

1. LINE Messaging API の設定
- LINE Developersコンソールでチャネルを作成
- Webhook URLとしてLambdaのAPIエンドポointを設定
- チャネルシークレットとチャネルアクセストークンを取得

2. AWS側の設定
- Lambda関数の作成とIAMロール設定
  - Amazon Bedrockへのアクセス権限
  - CloudWatch Logsへの書き込み権限
- API Gatewayの設定でLambdaをWebhookとして公開

3. Lambdaコードの実装

```python
import json
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage

# 環境変数から設定を読み込み
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID')

# LINE API クライアントの初期化
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

def invoke_bedrock(prompt):
    """Amazon Bedrockを呼び出して応答を生成"""
    llm = ChatBedrock(
        model_id=BEDROCK_MODEL_ID,
        model_kwargs={"max_tokens": 512},
    )
    messages = [
        SystemMessage(content="あなたは親切なAIアシスタントです"),
        HumanMessage(content=prompt)
    ]
    response = llm.invoke(messages)
    return response.content

def lambda_handler(event, context):
    """Lambda関数のメインハンドラー"""
    # LINE Webhookの署名検証
    signature = event['headers'].get('x-line-signature', '')
    body = event['body']

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid signature')
        }

    return {
        'statusCode': 200,
        'body': json.dumps('OK')
    }

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """テキストメッセージを受信したときの処理"""
    # ユーザーからのメッセージを取得
    user_message = event.message.text

    try:
        # Bedrockで応答を生成
        ai_response = invoke_bedrock(user_message)

        # LINE応答メッセージを作成
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=ai_response)
        )
    except Exception as e:
        # エラー時は一般的なメッセージを返す
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="申し訳ありません。エラーが発生しました。")
        )
        # CloudWatchにエラーログを出力
        print(f"Error: {str(e)}")

```

実装のポイントについて説明します：

1. 必要なライブラリ
- line-bot-sdk: LINE Messaging APIを扱うためのSDK
- langchain_aws: Amazon Bedrockを利用するためのライブラリ

2. 環境変数の設定
- LINE_CHANNEL_SECRET
- LINE_CHANNEL_ACCESS_TOKEN
- BEDROCK_MODEL_ID
これらはLambdaの環境変数として設定します。

3. 主な処理フロー
- LINEからのWebhookを受け取り、署名を検証
- テキストメッセージを抽出してBedrockに送信
- Bedrockからの応答をLINE APIで返信

4. エラーハンドリング
- LINE署名検証エラー
- Bedrock呼び出しエラー
- LINE API呼び出しエラー

デプロイ手順は以下の通りです：

1. 必要なパッケージをLambdaレイヤーとして追加
```bash
pip install line-bot-sdk langchain-aws -t python/lib/python3.9/site-packages/
zip -r layer.zip python/
```

2. AWS Lambdaの設定
- ランタイム: Python 3.9以上
- タイムアウト: 30秒程度
- メモリ: 256MB以上
- 環境変数の設定

3. API Gatewayの設定
- REST API作成
- LambdaプロキシインテグレーションでLambda関数と連携
- エンドポイントをLINE DevelopersコンソールのWebhook URLに設定
