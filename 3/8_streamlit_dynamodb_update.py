import streamlit as st
from langchain_aws import ChatBedrock
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage  # AIMessageを追加
from dotenv import load_dotenv
import os
import uuid
import time

load_dotenv()
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID")

st.title("Bedrock Chat")

# セッションステートの初期化
if "session_id" not in st.session_state:
    st.session_state.session_id = f"{str(uuid.uuid4())}_{int(time.time())}"

# DynamoDBの履歴オブジェクトの初期化
dynamo_history = DynamoDBChatMessageHistory(
    table_name="BedrockChatSessionTable",
    session_id=st.session_state.session_id,
    primary_key_name="Sessionid"
)

# 過去の会話履歴の読み込み
if "current_history" not in st.session_state:
    st.session_state.current_history = [
        {"type": "user" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
        for msg in dynamo_history.messages
    ]

if "chain" not in st.session_state:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant. Previous conversation context is provided for continuity."),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="human_message")
        ]
    )
    llm = ChatBedrock(
        model_id=BEDROCK_MODEL_ID,
        model_kwargs={"max_tokens": 512, "temperature": 0.7},
        streaming=True
    )
    st.session_state.chain = prompt | llm

# セッションIDの表示
st.sidebar.text(f"Session ID: {st.session_state.session_id}")

# 履歴クリアボタン
if st.button("Clear History"):
    st.session_state.current_history = []
    dynamo_history.clear()
    st.rerun()

# 現在のセッションの履歴を表示
for message in st.session_state.current_history:
    with st.chat_message(message["type"]):
        st.markdown(message["content"])

# ユーザー入力の処理
user_input = st.chat_input("Enter your question.")

if user_input:
    try:
        # ユーザーメッセージを追加
        user_message = {"type": "user", "content": user_input}
        st.session_state.current_history.append(user_message)
        dynamo_history.add_user_message(user_input)

        # ユーザーメッセージを表示
        with st.chat_message("user"):
            st.markdown(user_input)

        # LLMのレスポンスを取得
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            response_content = []

            # メッセージ履歴を適切な形式に変換
            message_history = [
                HumanMessage(content=msg["content"]) if msg["type"] == "user"
                else AIMessage(content=msg["content"])
                for msg in st.session_state.current_history[:-1]  # 最新のユーザーメッセージを除外
            ]

            # ストリーミングされたレスポンスを処理
            for chunk in st.session_state.chain.stream(
                {
                    "messages": message_history,
                    "human_message": [HumanMessage(content=user_input)]
                }
            ):
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                response_content.append(content)
                message_placeholder.markdown(''.join(response_content))

            # 完全なレスポンスを履歴に追加
            final_response = ''.join(response_content)
            ai_message = {"type": "assistant", "content": final_response}
            st.session_state.current_history.append(ai_message)
            dynamo_history.add_ai_message(final_response)

    except Exception as e:
        st.error(f"Error processing message: {str(e)}")
