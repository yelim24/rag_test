import streamlit as st
import time
from utils.llm_utils import with_message_history, return_counseling_sinario
from utils.constants import INITIAL_PROMPT, SYSTEM_MESSAGE, RESPONSE_ERROR_MSG

if "messages" not in st.session_state:
    st.session_state.messages = INITIAL_PROMPT

# 기존 메시지를 출력
st.write(st.session_state.key)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("당신의 고민을 말씀해주세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 사용자 메시지 출력
    with st.chat_message("user"):
        st.markdown(prompt)

    # 상담 시나리오 호출
    counseling_sinario = return_counseling_sinario(prompt)
    st.markdown(st.query_params["first_key"])
    # with_message_history 실행
    response = with_message_history.invoke(
        {
            "system_msg": SYSTEM_MESSAGE,
            "counseling_sinario": counseling_sinario,
            "human_msg": prompt,
        },
        config={"configurable": {"user_id": "st_test_4", "project_id": "chatbot-test-443801"}},
    )

    # 챗봇 응답 출력
    try:
        bot_response = response.content
    except:
        bot_response = RESPONSE_ERROR_MSG
        
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        chars = ''
        for char in bot_response:
            time.sleep(0.001)
            chars += char
            message_placeholder.markdown(chars + "▌")

        message_placeholder.markdown(bot_response)

    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    