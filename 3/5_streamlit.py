import streamlit as st
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID")

st.title("Bedrock Chatbot")

chat = ChatBedrock(
    model_id=BEDROCK_MODEL_ID,
    model_kwargs={"max_tokens": 1024},
    streaming=True,
)

messages = [
    SystemMessage(content="ユーザーの質問に正確に回答して下さい。")
]

if prompt := st.chat_input("質問を入力してください。"):
    messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        response = st.write_stream(chat.stream(messages))
    messages.append(response)
