import boto3
import json

session = boto3.Session(profile_name="AdministratorAccess-207567758619")
bedrock_runtime = session.client("bedrock-runtime", region_name="us-east-1")

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
    # ストリーミングレスポンスを取得。 bodyは、EventStreamオブジェクト
    response = bedrock_runtime.invoke_model_with_response_stream(
        body=json.dumps(body),
        modelId=modelId,
        accept="application/json",
        contentType="application/json"
    )
    print(f"response:\n{response}")
    """print(response)
    {
        'ResponseMetadata': {
            'RequestId': 'ebc07f21-911c-4e5f-863c-a80bd4cd19b0',
            'HTTPStatusCode': 200,
            'HTTPHeaders': {'date': 'Sat, 26 Oct 2024 10:12:26 GMT', 'content-type': 'application/vnd.amazon.eventstream', 'transfer-encoding': 'chunked', 'connection': 'keep-alive', 'x-amzn-requestid': 'ebc07f21-911c-4e5f-863c-a80bd4cd19b0', 'x-amzn-bedrock-content-type': 'application/json'},
            'RetryAttempts': 0
        },
        'contentType': 'application/json',
        'body': <botocore.eventstream.EventStream object at 0x106bb3890>
    }
    """
    
    print("=== ストリーミング開始 ===")
    # EventStreamの各チャンクをループ処理
    for event in response.get('body'):
        # チャンクのバイトデータを取得
        chunk_bytes = event['chunk']['bytes']
        # バイトデータをデコードしてJSONに変換
        chunk_json = json.loads(chunk_bytes.decode())

        print("\n--- 新しいチャンク ---")
        print(f"チャンクの型: {chunk_json.get('type')}")

        # チャンクの種類に応じて処理
        if chunk_json.get('type') == 'content_block_delta':
            text = chunk_json['delta']['text']
            print(f"テキスト内容: {text}")
        elif chunk_json.get('type') == 'message_delta':
            if 'text' in chunk_json.get('delta', {}):
                text = chunk_json['delta']['text']
                print(f"テキスト内容: {text}")

    print("\n=== ストリーミング終了 ===")

except Exception as e:
    print(f"エラーが発生しました: {e}")
