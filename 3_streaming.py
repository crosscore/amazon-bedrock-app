import boto3
import json

# create boto3 session
session = boto3.Session(profile_name="AdministratorAccess-207567758619")

# create Bedrock Runtime Client
bedrock_runtime = session.client("bedrock-runtime", region_name="us-east-1")

# define request body
body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 256,
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Amazon Bedrockという名称の由来を200文字以内で教えて"
                }
            ]
        }
    ]
}

modelId = "anthropic.claude-3-5-sonnet-20240620-v1:0"

try:
    # invoke_model with streaming
    response = bedrock_runtime.invoke_model_with_response_stream(
        body=json.dumps(body),
        modelId=modelId,
        accept="application/json",
        contentType="application/json"
    )

    # ストリームからチャンクを読み取って処理
    for event in response.get('body'):
        # バイトデータをJSONに変換
        chunk = json.loads(event['chunk']['bytes'].decode())

        # チャンクから必要なテキストを抽出して表示
        if chunk.get('type') == 'content_block_delta':
            print(chunk['delta']['text'], end='', flush=True)
        elif chunk.get('type') == 'message_delta':
            if 'text' in chunk.get('delta', {}):
                print(chunk['delta']['text'], end='', flush=True)

    print()  # 最後に改行を入れる

except Exception as e:
    print(f"エラーが発生しました: {e}")
