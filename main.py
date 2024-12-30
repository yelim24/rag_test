import streamlit as st
import time
from utils.llm_utils import with_message_history, return_counseling_sinario
from utils.constants import INITIAL_PROMPT, SYSTEM_MESSAGE, RESPONSE_ERROR_MSG

# 사용자 식별자 설정 (예: 로그인 또는 고유 ID)
USER_ID = st.query_params["user_id"]  # 예제에서는 입력을 사용
messages_key = f"messages_{USER_ID}"  # 사용자별 메시지 키 생성

# 디버깅용 세션 상태 출력
for key in st.session_state.keys():
    st.write(f"Key: {key}, Value: {st.session_state[key]}")

# 사용자별 메시지 상태 초기화
if messages_key not in st.session_state:
    st.session_state[messages_key] = INITIAL_PROMPT.copy()  # 기본값 설정

# 기존 메시지를 출력
for message in st.session_state[messages_key]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("당신의 고민을 말씀해주세요"):
    st.session_state[messages_key].append({"role": "user", "content": prompt})  # 사용자별 메시지 키 사용

    # 사용자 메시지 출력
    with st.chat_message("user"):
        st.markdown(prompt)

    # 상담 시나리오 호출
    counseling_sinario = return_counseling_sinario(prompt)

    # with_message_history 실행
    response = with_message_history.invoke(
        {
            "system_msg": SYSTEM_MESSAGE,
            "counseling_sinario": counseling_sinario,
            "human_msg": prompt,
        },
        config={"configurable": {"user_id": USER_ID, "project_id": "chatbot-test-443801"}},
    )

    # 챗봇 응답 출력
    try:
        bot_response = response.content
    except Exception as e:
        bot_response = RESPONSE_ERROR_MSG
        st.error(f"Error: {e}")

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        chars = ''
        for char in bot_response:
            time.sleep(0.001)
            chars += char
            message_placeholder.markdown(chars + "▌")

        message_placeholder.markdown(bot_response)

    st.session_state[messages_key].append({"role": "assistant", "content": bot_response})  # 사용자별 메시지 키 사용
    