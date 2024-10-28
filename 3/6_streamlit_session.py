import streamlit as st
from langchain_aws import ChatBedrock
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()
BEADLOCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID")

st.title("Bedrock Chatbot")

llm = ChatBedrock(
    model_id=BEADLOCK_MODEL_ID,
    model_kwargs={"max_tokens": 256},
    streaming=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="ユーザーの質問に正確に回答して下さい。")
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)

# chat logic
if prompt := st.chat_input("質問を入力してください。"):
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        response = st.write_stream(llm.stream(st.session_state.messages))
    st.session_state.messages.append(AIMessage(content=response))
