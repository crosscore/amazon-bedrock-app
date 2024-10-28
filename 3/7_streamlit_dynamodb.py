import streamlit as st
from langchain_aws import ChatBedrock
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
import os

load_dotenv()
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID")

st.title("Bedrock Chat")

if "session_id" not in st.session_state:
    st.session_state.session_id = "session_id"

if "history" not in st.session_state:
    st.session_state.history = DynamoDBChatMessageHistory(
        table_name="BedrockChatSessionTable",
        session_id=st.session_state.session_id,
    )

if "chain" not in st.session_state:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful chatbot"),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="human_message")
        ]
    )
    llm = ChatBedrock(model_id=BEDROCK_MODEL_ID)
    st.session_state.chain = prompt | llm
