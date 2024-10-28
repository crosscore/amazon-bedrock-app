import streamlit as st
from langchain_aws import ChatBedrock
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
import uuid

# 環境変数の読み込み
load_dotenv()
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID")

# タイトルの設定
st.title("Bedrock Chat")

# セッションステートの初期化
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "history" not in st.session_state:
    st.session_state.history = DynamoDBChatMessageHistory(
        table_name="BedrockChatSessionTable",
        session_id=st.session_state.session_id,
        primary_key_name="Sessionid"  # パーティションキー名を正しく設定
    )

if "chain" not in st.session_state:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="human_message")
        ]
    )
    llm = ChatBedrock(
        model_id=BEDROCK_MODEL_ID,
        model_kwargs={"max_tokens": 512},
        streaming=True
    )
    st.session_state.chain = prompt | llm

# セッションIDの表示（デバッグ用）
st.sidebar.text(f"Session ID: {st.session_state.session_id}")

# 履歴をクリアするボタン
if st.button("Clear History"):
    st.session_state.history.clear()
    st.experimental_rerun()

# チャットメッセージの表示
try:
    for message in st.session_state.history.messages:
        with st.chat_message(message.type):
            st.markdown(message.content)
except Exception as e:
    st.error(f"Error loading messages: {str(e)}")

# ユーザー入力の処理
user_input = st.chat_input("Enter your question.")

if user_input:
    try:
        # ユーザーのメッセージを履歴に追加
        st.session_state.history.add_user_message(user_input)

        # ユーザーメッセージを表示
        with st.chat_message("user"):
            st.markdown(user_input)

        # LLMのレスポンスを取得
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            response_content = []

            # ストリーミングされたレスポンスを処理
            for chunk in st.session_state.chain.stream(
                {
                    "messages": st.session_state.history.messages,
                    "human_message": [HumanMessage(content=user_input)]
                }
            ):
                # チャンクの内容を抽出して追加
                if hasattr(chunk, 'content'):
                    content = chunk.content
                else:
                    content = str(chunk)
                response_content.append(content)
                message_placeholder.markdown(''.join(response_content))

            # 完全なレスポンスを履歴に追加
            final_response = ''.join(response_content)
            st.session_state.history.add_ai_message(final_response)

    except Exception as e:
        st.error(f"Error processing message: {str(e)}")
