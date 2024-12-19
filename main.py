import streamlit as st
import json
from google.cloud import firestore
from google.oauth2 import service_account
from google.cloud import firestore
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory, ConfigurableFieldSpec
from langchain_google_firestore import FirestoreChatMessageHistory, CustomFirestoreChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import time

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

def return_counseling_sinario(user_input, k=3):

    embedding_model_name = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"
    embeddings_model = HuggingFaceEmbeddings(
                        model_name=embedding_model_name,
                        model_kwargs={'device':"cpu"},
                        encode_kwargs={'normalize_embeddings':True})

    collection_name = "question_answer2" # 추후 디비 변경 필요
    db_dir = "./db/chromadb"

    # Chroma DB 로드
    vector_db = Chroma(
        persist_directory=db_dir,
        embedding_function=embeddings_model,
        collection_name=collection_name)
    
    retriever = vector_db.as_retriever(search_kwargs={"k": k})
    
    docs = retriever.invoke(user_input)
    
    results = [f"내담자: {doc.page_content}\n상담사: {doc.metadata['answer']}"for doc in docs]
    
    return "\n\n".join(results)

system_prompt_template = """{system_msg}

#상담 예시
{counseling_sinario}

#내담자 정보
조카를 걱정하는 20대 여성
"""

system_message = """당신은 정신 건강 상담사입니다.
아래 상담 예시와 내담자 정보를 참고해서 친절한 말투로 사용자에게 응원, 공감, 안정, 조언을 해주세요.
답변은 짧게 작성해주세요."""

llm = ChatOpenAI(model="gpt-4o-mini")

prompt  = ChatPromptTemplate.from_messages([
    ("system", system_prompt_template),
    MessagesPlaceholder(variable_name="history", optional=True), # n_messages=1
    ("human", "{human_msg}")
])

runnable  = prompt | llm

def get_session_history(user_id, project_id):
    client = firestore.Client(
        project=project_id)

    firestore_chat_history = CustomFirestoreChatMessageHistory(
        session_id=user_id,
        collection="chat_logs",
        client=client)

    return firestore_chat_history

with_message_history = RunnableWithMessageHistory(
    runnable,
    get_session_history,
    input_messages_key="human_msg",
    history_messages_key="history",
    history_factory_config=[  # 기존의 "session_id" 설정을 대체하게 됩니다.
        ConfigurableFieldSpec(
            id="user_id",  # get_session_history 함수의 첫 번째 인자로 사용됩니다.
            annotation=str,
            name="User ID",
            description="사용자의 고유 식별자입니다.",
            default="",
            is_shared=True,
        ),
        ConfigurableFieldSpec(
            id="project_id",  # get_session_history 함수의 두 번째 인자로 사용됩니다.
            annotation=str,
            name="Project ID",
            description="Firestore Project ID입니다.",
            default="",
            is_shared=True,
        ),
    ],
)


if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 메시지를 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("당신의 고민을 말씀해주세요"):
    user_instruction = ''
    if st.session_state.messages != []:
        user_instruction = "(사용자가 적극적으로 표현할 수 있도록 대화를 진행해주세요)"
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 사용자 메시지 출력
    with st.chat_message("user"):
        st.markdown(prompt)

    # 상담 시나리오 호출
    counseling_sinario = return_counseling_sinario(prompt)

    # with_message_history 실행
    response = with_message_history.invoke(
        {
            "system_msg": system_message,
            "counseling_sinario": counseling_sinario,
            "human_msg": prompt
        },
        config={"configurable": {"user_id": "st_test_1", "project_id": "chatbot-test-443801"}},
    )

    # 챗봇 응답 출력
    bot_response = response.content  # response.content를 Streamlit에 연결
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        chars = ''
        for char in bot_response:
            time.sleep(0.001)  # 지연 효과
            chars += char
            message_placeholder.markdown(chars + "▌")

        message_placeholder.markdown(bot_response)

    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    