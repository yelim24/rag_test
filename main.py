import streamlit as st
import json
from google.cloud import firestore
from google.oauth2 import service_account


st.markdown("#### 채팅 테스트")
st.write("채팅 테스트")

# Authenticate to Firestore
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="chatbot-test-443801")

# Create a reference to the Google post.
doc_ref = db.collection("chat_logs").document("241209-18test")

# Then get the data at that reference.
doc = doc_ref.get()

# Let's see what we got!
st.write("The id is: ", doc.id)
st.write("The contents are: ", doc.to_dict())


# Chroma DB에서 상담 시나리오 작성
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

def return_counseling_sinario(user_input, k=3):
    """
    상담 시나리오를 반환하는 함수.

    Parameters:
        user_input (str): 사용자 입력.
        k (int, optional): 검색할 문서의 개수. 기본값은 3.
    
    Returns:
        str: 검색 결과.
    """
    embedding_model_name = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"
    embeddings_model = HuggingFaceEmbeddings(
                        model_name=embedding_model_name,
                        model_kwargs={'device':"cpu"},
                        encode_kwargs={'normalize_embeddings':True})

    collection_name = "question_answer2"
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


st.write(return_counseling_sinario("애들이 불쌍해"))