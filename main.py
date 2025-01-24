import streamlit as st
import time
# from utils.llm_utils import with_message_history, return_counseling_scenario
from utils.llm_utils import return_counseling_scenario
from utils.constants import INITIAL_PROMPT, PROMPT_TEMPLATE, RESPONSE_ERROR_MSG
from utils.firestore_utils import get_session_history, delete_session_history
from utils.llm_utils import get_chat_chain

# 사용자 식별자 설정 (예: 로그인 또는 고유 ID)
USER_ID = st.query_params.get("user_id", "default_user")
messages_key = f"messages_{USER_ID}"  # 사용자별 메시지 키 생성

st.subheader("prompt 테스트용 페이지입니다.")

# 대화 초기화 버튼 추가
if st.button("대화 기록 삭제"):
    # Streamlit 세션 상태 초기화
    st.session_state.messages = []
    # Firestore 대화 기록 삭제
    delete_session_history(USER_ID, "chatbot-test-443801")
    st.rerun()

hf_endpoint_url = st.text_input("HuggingFace Endpoint URL", "")

custom_prompt = st.text_area(
    "하단에 테스트용 프롬프트를 입력하세요.",
    height=150
)

if custom_prompt == '':
    st.session_state.custom_prompt = PROMPT_TEMPLATE
else:
    st.session_state.custom_prompt = custom_prompt

with st.chat_message(INITIAL_PROMPT[0]["role"]):
    st.markdown(INITIAL_PROMPT[0]["content"])
    
if "messages" not in st.session_state:
        st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
            
# 사용자 입력 처리
if prompt := st.chat_input("당신의 고민을 말씀해주세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})  # 사용자별 메시지 키 사용

    # 사용자 메시지 출력
    with st.chat_message("user"):
        st.markdown(prompt)

    # 상담 시나리오 호출
    # counseling_scenario = return_counseling_scenario(prompt)
    
    # # with_message_history 실행
    # response = with_message_history.invoke(
    #     {
    #         "counseling_scenario": counseling_scenario,
    #         "human_msg": prompt,
    #     },
    #     config={"configurable": {"user_id": USER_ID, "project_id": "chatbot-test-443801"}},
    # )
    
    # chat_chain 초기화
    chat_chain = get_chat_chain(st.session_state.custom_prompt, hf_endpoint_url)

    # 채팅 응답 생성
    response = chat_chain.invoke(
        {
            # "counseling_scenario": counseling_scenario,
            "human_msg": prompt,
        },
        config={"configurable": {"user_id": USER_ID, "project_id": "chatbot-test-443801"}},
    )
    
    if isinstance(response, str):
        bot_response = response
    else:
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

    st.session_state.messages.append({"role": "assistant", "content": bot_response})  # 사용자별 메시지 키 사용
    