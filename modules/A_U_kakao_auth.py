import streamlit as st
import os
import requests
import pandas as pd
from urllib.parse import urlencode, urlparse, parse_qs

KAKAO_REST_API_KEY = st.secrets["KAKAO_REST_API_KEY"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]
USER_DB = "data/kakao_users.csv"

# 로그인 버튼 출력
def render_kakao_login_button():
    auth_url = (
        f"https://kauth.kakao.com/oauth/authorize?"
        + urlencode({
            "response_type": "code",
            "client_id": KAKAO_REST_API_KEY,
            "redirect_uri": REDIRECT_URI,
        })
    )

    st.markdown(f"""
        <a href="{auth_url}">
            <img src="https://developers.kakao.com/assets/img/about/logos/kakaologin/kr/kakaolink_btn_medium.png"
                style="height: 45px;">
        </a>
    """, unsafe_allow_html=True)

# 인증 코드 콜백 처리
def handle_kakao_callback():
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"][0]

        # 토큰 요청
        token_url = "https://kauth.kakao.com/oauth/token"
        token_data = {
            "grant_type": "authorization_code",
            "client_id": KAKAO_REST_API_KEY,
            "redirect_uri": REDIRECT_URI,
            "code": code,
        }
        token_response = requests.post(token_url, data=token_data)
        access_token = token_response.json().get("access_token")

        if access_token:
            # 사용자 정보 요청
            user_info_url = "https://kapi.kakao.com/v2/user/me"
            headers = {"Authorization": f"Bearer {access_token}"}
            user_response = requests.get(user_info_url, headers=headers)
            user_json = user_response.json()

            kakao_id = user_json.get("id")
            profile = user_json.get("properties", {})
            nickname = profile.get("nickname")
            profile_image = profile.get("profile_image")

            user_data = {
                "kakao_id": kakao_id,
                "nickname": nickname,
                "profile_image": profile_image,
            }

            save_user_info(user_data)
            st.success(f"환영합니다, {nickname}님!")
            st.session_state["kakao_user"] = user_data

            # 쿼리 제거용 rerun
            st.experimental_set_query_params()

def render_logout_button():
    if "kakao_user" in st.session_state:
        if st.button("로그아웃"):
            del st.session_state["kakao_user"]
            st.experimental_rerun()
            
# 사용자 정보 CSV에 저장
def save_user_info(user_data):
    os.makedirs("data", exist_ok=True)
    try:
        df = pd.read_csv(USER_DB)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["kakao_id", "nickname", "profile_image"])

    if user_data["kakao_id"] not in df["kakao_id"].values:
        df = pd.concat([df, pd.DataFrame([user_data])], ignore_index=True)
        df.to_csv(USER_DB, index=False)
