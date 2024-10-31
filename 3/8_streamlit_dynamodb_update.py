import streamlit as st
from langchain_aws import ChatBedrock
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
import os
import uuid
import time
import json

# デバッグ出力用の関数
def debug_print_messages(title, messages):
    print("\n" + "="*50)
    print(f"DEBUG OUTPUT: {title}")
    print("="*50)
    for i, msg in enumerate(messages, 1):
        if isinstance(msg, (HumanMessage, AIMessage)):
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            content = msg.content
        elif isinstance(msg, dict):
            role = msg["type"]
            content = msg["content"]
        else:
            role = type(msg).__name__
            content = str(msg)

        print(f"\nMessage {i}:")
        print(f"Role: {role}")
        print(f"Content: {content}")
    print("="*50 + "\n")

# 会話履歴の制限数
MAX_HISTORY_LENGTH = 4  # 直近の4往復（8メッセージ）を保持

load_dotenv()
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID")

st.title("Bedrock Chat")

# セッションステートの初期化
if "session_id" not in st.session_state:
    st.session_state.session_id = f"{str(uuid.uuid4())}_{int(time.time())}"
    st.session_state.current_history = []

# DynamoDBの履歴オブジェクトの初期化
dynamo_history = DynamoDBChatMessageHistory(
    table_name="BedrockChatSessionTable",
    session_id=st.session_state.session_id,
    primary_key_name="Sessionid"
)

if "chain" not in st.session_state:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an AI assistant. Please help the user."),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="human_message")
        ]
    )
    llm = ChatBedrock(
        model_id=BEDROCK_MODEL_ID,
        model_kwargs={
            "max_tokens": 512,
            "temperature": 0.7,
        },
        streaming=True
    )
    st.session_state.chain = prompt | llm

# セッションIDの表示
st.sidebar.text(f"Session ID: {st.session_state.session_id}")
st.sidebar.text(f"Keeping last {MAX_HISTORY_LENGTH} conversation rounds")

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
        # 現在の全履歴をデバッグ出力
        debug_print_messages("Current Session History", st.session_state.current_history)

        # ユーザーメッセージを追加
        user_message = {"type": "user", "content": user_input}
        st.session_state.current_history.append(user_message)
        dynamo_history.add_user_message(user_input)

        # 履歴が長くなりすぎた場合、古いメッセージを削除
        if len(st.session_state.current_history) > MAX_HISTORY_LENGTH * 2:
            st.session_state.current_history = st.session_state.current_history[-MAX_HISTORY_LENGTH * 2:]

        # ユーザーメッセージを表示
        with st.chat_message("user"):
            st.markdown(user_input)

        # LLMのレスポンスを取得
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            response_content = []

            # 制限された履歴のみを使用
            message_history = [
                HumanMessage(content=msg["content"]) if msg["type"] == "user"
                else AIMessage(content=msg["content"])
                for msg in st.session_state.current_history[:-1]
            ]

            # LLMに送信される履歴をデバッグ出力
            limited_history = message_history[-MAX_HISTORY_LENGTH * 2:]
            debug_print_messages("Messages Being Sent to LLM", [
                ("system", "You are an AI assistant. Please help the user."),
                *limited_history,
                HumanMessage(content=user_input)
            ])

            # ストリーミングされたレスポンスを処理
            for chunk in st.session_state.chain.stream(
                {
                    "messages": limited_history,
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

            # 最終的なレスポンスをデバッグ出力
            print("\n" + "="*50)
            print("DEBUG OUTPUT: LLM Response")
            print("="*50)
            print(final_response)
            print("="*50 + "\n")

    except Exception as e:
        st.error(f"Error processing message: {str(e)}")
        # エラー時のデバッグ情報も出力
        print("\n" + "="*50)
        print("DEBUG OUTPUT: Error Information")
        print("="*50)
        print(f"Error: {str(e)}")
        print(f"Session ID: {st.session_state.session_id}")
        print(f"Current history length: {len(st.session_state.current_history)}")
        print("="*50 + "\n")
