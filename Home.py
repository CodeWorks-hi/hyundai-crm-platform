# 실행법 : streamlit run Home.py
# 서버 주소 : https://main-project-codeworks.streamlit.app/
# 대표 이미지: https://m.ddaily.co.kr/2022/07/28/2022072820411931122_l.png

import streamlit as st
import os
import logging
import traceback
import datetime


# 접속 로그 기록
logging.basicConfig(level=logging.INFO)
logging.info(f"[접속 기록] 페이지 접속 시각: {datetime.datetime.now()}")

# 페이지 설정
st.set_page_config(
    page_title="Hyundai & Kia ERP",
    layout="wide",
    page_icon="https://i.namu.wiki/i/uNKzeN4J5LmcBr_4EbF2D6ObllziCSQWNo8inXP6F2vS1zIb1UtVws-7AzkP0qOUrm40Um6xekuoFUYDMtFT3w.webp"
)

# 페이지 상태 초기화
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

# 페이지 전환 함수
def switch_page(page):
    st.session_state.current_page = page
    st.rerun()

# 홈 페이지 구성
if st.session_state.current_page == "home":
    st.image("images/hyundae_kia_logo.png", width=100)

    st.markdown(
        "<h1 style='text-align: center; margin-bottom: 40px;'>Hyundai & Kia ERP</h1>",
        unsafe_allow_html=True
    )

    col4, col1, col2, col3, col5 = st.columns([1.5, 1, 1, 1, 1])

    with col1:
        st.image("images/user_icon.png", width=80)
        st.markdown("### 일반회원\n개인 사용자 전용 서비스")
        if st.button("접속하기", key="btn_user"):
            switch_page("user_main")

    with col2:
        st.image("images/shop_icon.png", width=80)
        st.markdown("### 딜러 허브\n대리점 및 가맹점 서비스")
        if st.button("접속하기", key="btn_dealer"):
            switch_page("dealer_main")

    with col3:
        st.image("images/admin_icon.png", width=80)
        st.markdown("### 관리자 콘솔\n운영 및 데이터 관리")
        if st.button("접속하기", key="btn_admin"):
            switch_page("admin_main")

# 페이지 라우팅 처리
else:
    try:
        page = st.session_state.get("current_page")

        if page == "user_main":
            import A_U_main as auto
            auto.app()

        elif page == "A_U_comparison":
            import A_U_main as auto
            auto.app()  # 🔁 app 안에서 comparison 호출 포함

        elif page == "A_U_event":
            import A_U_main as auto
            auto.app()

        elif page == "A_U_support":
            import A_U_main as auto
            auto.app()

        elif page == "A_U_detail":
            import A_U_detail as detail
            detail.detail_ui()


            
    except Exception as e:
        st.error("⚠️ 페이지 로딩 중 오류가 발생했습니다.")
        st.exception(e)


# 푸터
st.markdown("---")
st.markdown(
    '''
    <div style='text-align: center; color: gray; font-size: 0.9rem; margin-top: 30px;'>
        © 2025 Hyundai & Kia Export Dashboard. All rights reserved.
    </div>
    ''',
    unsafe_allow_html=True
)
