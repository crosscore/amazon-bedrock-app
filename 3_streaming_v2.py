import boto3
import json

session = boto3.Session(profile_name="AdministratorAccess-207567758619")
bedrock_runtime = session.client("bedrock-runtime", region_name="us-east-1")

body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 512,
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Amazon Bedrockという名称の由来を300文字以内で教えて"
                }
            ]
        }
    ]
}

modelId = "anthropic.claude-3-5-sonnet-20240620-v1:0"

try:
    response = bedrock_runtime.invoke_model_with_response_stream(
        body=json.dumps(body),
        modelId=modelId,
        accept="application/json",
        contentType="application/json"
    )
    print(f"response:\n{response}")

    print("=== ストリーミング開始 ===")
    for event in response.get('body'):
        chunk_bytes = event['chunk']['bytes']
        chunk_json = json.loads(chunk_bytes.decode())

        if chunk_json.get('type') == 'content_block_delta':
            text = chunk_json['delta']['text']
            print(text, end="", flush=True)
        elif chunk_json.get('type') == 'message_delta':
            if 'text' in chunk_json.get('delta', {}):
                text = chunk_json['delta']['text']
                print(text, end="", flush=True)

    print("\n=== ストリーミング終了 ===")

except Exception as e:
    print(f"エラーが発生しました: {e}")
