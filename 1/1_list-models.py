import boto3
import logging
from dotenv import load_dotenv
import os

load_dotenv()
AWS_PROFILE = os.getenv('AWS_PROFILE')

boto3.set_stream_logger('boto3.resources', logging.DEBUG)

session = boto3.Session(profile_name=AWS_PROFILE)

# create Bedrock client
bedrock = boto3.client("bedrock")

# list available models
result = bedrock.list_foundation_models()
print(result)
