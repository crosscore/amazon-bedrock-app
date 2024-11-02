import json
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage

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
