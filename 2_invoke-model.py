import boto3
import json

# 特定のプロファイルを使用してセッションを作成
session = boto3.Session(profile_name="AdministratorAccess-207567758619")

# Bedrock Runtimeクライアントを作成
bedrock_runtime = session.client("bedrock-runtime", region_name="us-east-1")

# リクエストボディの定義
body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 128,
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Amazon Bedrockという名称の由来を100文字以内で教えて"
                }
            ]
        }
    ]
}

modelId = "anthropic.claude-3-5-sonnet-20240620-v1:0"

try:
    # モデルを呼び出す
    response = bedrock_runtime.invoke_model(
        body=json.dumps(body),
        modelId=modelId,
        accept="application/json",
        contentType="application/json"
    )

    # レスポンスの処理
    response_body = json.loads(response['body'].read())
    answer = response_body["content"][0]["text"]
    print(answer)

except Exception as e:
    print(f"エラーが発生しました: {e}")
