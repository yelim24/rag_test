import streamlit as st
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnableWithMessageHistory, ConfigurableFieldSpec
from utils.firestore_utils import get_session_history
from utils.constants import PROMPT_TEMPLATE

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

def return_counseling_scenario(user_input, k=3):
    embedding_model_name = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"
    embeddings_model = HuggingFaceEmbeddings(
        model_name=embedding_model_name,
        model_kwargs={'device': "cpu"},
        encode_kwargs={'normalize_embeddings': True},
    )

    collection_name = "question_answer1" # 추후 디비 변경 필요
    db_dir = "./db/chromadb"

    # Chroma DB 로드
    vector_db = Chroma(
        persist_directory=db_dir,
        embedding_function=embeddings_model,
        collection_name=collection_name)
        
    retriever = vector_db.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(user_input)
    results = [
        f"내담자: {doc.page_content}\n상담사: {doc.metadata['answer']}"
        for doc in docs
    ]
    return "\n\n".join(results)

# llm = ChatOpenAI(model="gpt-4o-mini", api_key=st.secrets["OPENAI_API_KEY"])

# prompt = ChatPromptTemplate.from_messages([
#     ("system", PROMPT_TEMPLATE),
#     MessagesPlaceholder(variable_name="history", optional=True),
#     ("human", "{human_msg}")
# ])

# runnable = prompt | llm

# with_message_history = RunnableWithMessageHistory(
#     runnable,
#     get_session_history,
#     input_messages_key="human_msg",
#     history_messages_key="history",
#     history_factory_config=[  # 기존의 "session_id" 설정을 대체하게 됩니다.
#         ConfigurableFieldSpec(
#             id="user_id",  # get_session_history 함수의 첫 번째 인자로 사용됩니다.
#             annotation=str,
#             name="User ID",
#             description="사용자의 고유 식별자입니다.",
#             default="",
#             is_shared=True,
#         ),
#         ConfigurableFieldSpec(
#             id="project_id",  # get_session_history 함수의 두 번째 인자로 사용됩니다.
#             annotation=str,
#             name="Project ID",
#             description="Firestore Project ID입니다.",
#             default="",
#             is_shared=True,
#         ),
#     ],
# )


def get_chat_chain(custom_prompt):
    """채팅 체인을 생성하는 함수"""
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=st.secrets["OPENAI_API_KEY"])

    prompt = ChatPromptTemplate.from_messages([
        ("system", custom_prompt),
        MessagesPlaceholder(variable_name="history", optional=True),
        ("human", "{human_msg}")
    ])

    runnable = prompt | llm

    return RunnableWithMessageHistory(
        runnable,
        get_session_history,
        input_messages_key="human_msg",
        history_messages_key="history",
        history_factory_config=[
            ConfigurableFieldSpec(
                id="user_id",
                annotation=str,
                name="User ID",
                description="사용자의 고유 식별자입니다.",
                default="",
                is_shared=True,
            ),
            ConfigurableFieldSpec(
                id="project_id",
                annotation=str,
                name="Project ID",
                description="Firestore Project ID입니다.",
                default="",
                is_shared=True,
            ),
        ],
    )