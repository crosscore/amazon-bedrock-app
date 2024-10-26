import boto3
import json

# create boto3 session
session = boto3.Session(profile_name="AdministratorAccess-207567758619")

# create Bedrock Runtime Client
bedrock_runtime = session.client("bedrock-runtime", region_name="us-east-1")

# difine request body
body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 128,
    #"system": "You are a helpful assistant.",
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
    # invoke_model
    response = bedrock_runtime.invoke_model(
        body=json.dumps(body),
        modelId=modelId,
        accept="application/json",
        contentType="application/json"
    )

    response_body = json.loads(response['body'].read())
    answer = response_body["content"][0]["text"]
    print(answer)

except Exception as e:
    print(f"An error has occurred: {e}")
