import boto3
import json
from dotenv import load_dotenv
import os

load_dotenv()
AWS_PROFILE = os.getenv('AWS_PROFILE')
AWS_REGION = os.getenv('AWS_REGION')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID')

# create boto3 session
session = boto3.Session(profile_name=AWS_PROFILE)

# create Bedrock Runtime Client
bedrock_runtime = session.client("bedrock-runtime", region_name=AWS_REGION)

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

try:
    # invoke_model
    response = bedrock_runtime.invoke_model(
        body=json.dumps(body),
        modelId=BEDROCK_MODEL_ID,
        accept="application/json",
        contentType="application/json"
    )

    response_body = json.loads(response['body'].read())
    answer = response_body["content"][0]["text"]
    print(answer)

except Exception as e:
    print(f"An error has occurred: {e}")
