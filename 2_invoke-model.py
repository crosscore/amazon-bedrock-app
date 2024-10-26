import boto3
import json
import time
from botocore.exceptions import ClientError

def invoke_model_with_retry(bedrock_runtime, body, modelId, max_retries=5, initial_delay=1):
    for attempt in range(max_retries):
        try:
            response = bedrock_runtime.invoke_model(
                body=body,
                modelId=modelId,
                accept="application/json",
                contentType="application/json"
            )
            return response
        except ClientError as e:
            if e.response['Error']['Code'] == 'ThrottlingException':
                if attempt == max_retries - 1: # when last attempt
                    raise
                wait_time = initial_delay * (2 ** attempt)  # 指数バックオフ
                print(f"waiting for retry ... {wait_time} second")
                time.sleep(wait_time)
            else:
                raise

bedrock_runtime = boto3.client("bedrock-runtime")

body = json.dumps({
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 64,
    "messages": [
        {
            "role": "user",
            "content": "Amazon Bedrockという名称の由来は？",
        }
    ],
})

modelId = "anthropic.claude-3-sonnet-20240229-v1:0"

try:
    response = invoke_model_with_retry(bedrock_runtime, body, modelId)
    response_body = json.loads(response.get("body").read())
    answer = response_body["content"][0]["text"]
    print(answer)
except Exception as e:
    print(f"Error has occurred: {e}")
