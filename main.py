import streamlit as st
import json
from openai import OpenAI
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