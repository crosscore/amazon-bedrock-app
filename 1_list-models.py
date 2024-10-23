import boto3

# create Bedrock client
bedrock = boto3.client("bedrock")

# list available models
result = bedrock.list_foundation_models()
print(result)
