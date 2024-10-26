import boto3
import logging

boto3.set_stream_logger('boto3.resources', logging.DEBUG)

# create Bedrock client
bedrock = boto3.client("bedrock")

# list available models
result = bedrock.list_foundation_models()
print(result)
