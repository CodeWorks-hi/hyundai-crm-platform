import streamlit as st

# 본인의 카카오톡 채널 ID 입력
channel_public_id = "_xfxhjXn"  # 올바른 채널 ID 반영


import os
import streamlit as st
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# 로그인 버튼 출력
def render_kakao_login_button():
    params = {
        "client_id": KAKAO_REST_API_KEY,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code"
    }
    auth_url = f"https://kauth.kakao.com/oauth/authorize?{urlencode(params)}"
    st.markdown(f"[카카오 로그인]({auth_url})", unsafe_allow_html=True)

# 인가 코드 처리 (카카오가 콜백 보낼 때)
def handle_kakao_callback():
    query_params = st.query_params
    code = query_params.get("code")

    if code:
        st.success("로그인 인가 코드 수신 완료")
        st.write("인가 코드:", code)

        # 여기서 토큰 교환 API 연동 가능
        # access_token = get_access_token(code)

