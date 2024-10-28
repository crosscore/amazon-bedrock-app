from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os
import os

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY,
    max_tokens=256,
    streaming=True
)

messages = [
    SystemMessage(content="あなたは親切なAIアシスタントです"),
    HumanMessage(content="Amazon Bedrockの名称の由来を200文字以内で教えて")
]

try:
    for chunk in llm.stream(messages):
        print(chunk.content, end="", flush=True)

except Exception as e:
    print(f"エラーが発生しました: {e}")
