import streamlit as st
import json
from google.cloud import firestore
from google.oauth2 import service_account
from datetime import datetime
import pytz
from langchain_google_firestore import FirestoreChatMessageHistory

class CustomFirestoreChatMessageHistory(FirestoreChatMessageHistory):
    def add_message(self, message):
        self.messages.append(message)
        self._upsert_message(message)

    def _upsert_message(self, message):
        kst_now = datetime.now(pytz.timezone('Asia/Seoul'))

        if self.encode_message:
            encoded_message = message.json().encode()
            text_message = {
                "type": getattr(message, "type", "unknown"),
                "content": message.content,
                "timestamp": kst_now,
            }

            update_data = {
                "messages": firestore.ArrayUnion([encoded_message]),
                "text_messages": firestore.ArrayUnion([text_message]),
            }
        else:
            update_data = {
                "messages": firestore.ArrayUnion([message.json()]),
            }

        self.doc_ref.set(update_data, merge=True)

    def get_st_messages(self):
        """Firestore에서 메시지를 가져와서 Streamlit 채팅 형식으로 변환"""
        messages = []
        doc = self.doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            if 'text_messages' in data:
                for msg in data['text_messages']:
                    role = "assistant" if msg["type"] == "ai" else "user"
                    messages.append({
                        "role": role,
                        "content": msg["content"]
                    })
        
        return messages if messages else []

def get_session_history(user_id, project_id):
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    client = firestore.Client(credentials=creds, project=project_id)

    return CustomFirestoreChatMessageHistory(
        session_id=user_id,
        collection="chat_logs",
        client=client,
    )
    