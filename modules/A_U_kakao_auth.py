import streamlit as st
import os
import requests
import pandas as pd
from urllib.parse import urlencode, urlparse, parse_qs
import base64

KAKAO_REST_API_KEY = st.secrets["KAKAO_REST_API_KEY"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]
USER_DB = "data/kakao_users.csv"
# +------------+
# | 카카오 로그인 |
# +------------+
# 로그인 버튼 출력




def load_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_base64 = load_base64_image("images/kakao_login_btn.png")   


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
            <img src="data:image/png;base64,{img_base64}" style="height: 45px;">
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
def render_user_profile_or_form():
    if "kakao_user" not in st.session_state:
        return

    user = st.session_state["kakao_user"]
    if is_user_info_complete(user["kakao_id"]):
        st.success("추가 정보가 이미 등록되어 있습니다.")
        show_user_summary()
    else:
        render_signup_form()

def show_user_summary():
    df = pd.read_csv(USER_DB)
    row = df[df["kakao_id"] == st.session_state["kakao_user"]["kakao_id"]]
    if not row.empty:
        st.image(row.iloc[0]["profile_image"], width=80)
        st.markdown(f"""
            **닉네임**: {row.iloc[0]['nickname']}  
            **성별**: {row.iloc[0]['gender']}  
            **출생 연도**: {row.iloc[0]['birth_year']}  
            **관심 차종**: {row.iloc[0]['car_interest']}  
        """)
        
def render_signup_form():
    if "kakao_user" not in st.session_state:
        st.warning("로그인 후 이용 가능합니다.")
        return

    user = st.session_state["kakao_user"]
    st.subheader("회원 추가 정보 입력")

    with st.form("signup_form"):
        gender = st.radio("성별", ["남성", "여성"], horizontal=True)
        birth_year = st.selectbox("출생 연도", list(range(1960, 2010))[::-1])
        car_interest = st.multiselect("관심 차종", ["쏘나타", "그랜저", "캐스퍼", "투싼", "아이오닉5", "기타"])

        submitted = st.form_submit_button("저장하기")
        if submitted:
            save_user_info_extended(user, gender, birth_year, car_interest)
            st.success("추가 정보가 저장되었습니다.")

def save_user_info_extended(user_data, gender, birth_year, car_interest):
    os.makedirs("data", exist_ok=True)
    try:
        df = pd.read_csv(USER_DB)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["kakao_id", "nickname", "profile_image", "gender", "birth_year", "car_interest"])

    # 이미 존재하는 사용자인 경우 업데이트
    existing_index = df[df["kakao_id"] == user_data["kakao_id"]].index
    new_row = {
        "kakao_id": user_data["kakao_id"],
        "nickname": user_data["nickname"],
        "profile_image": user_data["profile_image"],
        "gender": gender,
        "birth_year": birth_year,
        "car_interest": ", ".join(car_interest),
    }

    if len(existing_index) > 0:
        df.loc[existing_index[0]] = new_row
    else:
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df.to_csv(USER_DB, index=False)


def is_user_info_complete(user_id):
    try:
        df = pd.read_csv(USER_DB)
        row = df[df["kakao_id"] == user_id]
        return not row[["gender", "birth_year", "car_interest"]].isnull().values.any()
    except:
        return False