from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID')

llm = ChatBedrock(
    model_id=BEDROCK_MODEL_ID,
    model_kwargs={"max_tokens": 128},
)

messages = [
    SystemMessage(content="あなたは親切なAIアシスタントです"),
    HumanMessage(content="Amazon Bedrockの名称の由来を100文字以内で教えて")
]

try:
    response = llm.invoke(messages)
    print(response.content)

except Exception as e:
    print(f"エラーが発生しました: {e}")
