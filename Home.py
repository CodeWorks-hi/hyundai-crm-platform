# 실행법 : streamlit run Home.py
# 서버 주소 : https://main-project-codeworks.streamlit.app/
# https://m.ddaily.co.kr/2022/07/28/2022072820411931122_l.png

import streamlit as st
import os
# 파피콘 이랑 인터넷 텝 글씨 
st.set_page_config(page_title="Hyundai & Kia ERP", layout="wide", 
                   page_icon="https://i.namu.wiki/i/uNKzeN4J5LmcBr_4EbF2D6ObllziCSQWNo8inXP6F2vS1zIb1UtVws-7AzkP0qOUrm40Um6xekuoFUYDMtFT3w.webp")


# 페이지 초기화
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

# 페이지 전환 함수
def switch_page(page):
    st.session_state.current_page = page
    st.rerun()  # 즉시 리렌더링

# 페이지 분기
if st.session_state.current_page == "home":
    # 로고 이미지 표시 (로컬 이미지)
    st.image("images/hyundae_kia_logo.png", width=100)

    # 제목 표시
    st.markdown(
        "<h1 style='text-align: center; margin-bottom: 40px;'>Hyundai & Kia ERP</h1>",
        unsafe_allow_html=True
    )

    # 컬럼 구분 4는 여백 1 2 3 버튼 있는 이미지 5 여백
    col4, col1, col2, col3,col5= st.columns([1.5,1,1,1,1])

    with col4:
        st.subheader("")
    with col5:
        st.subheader("")

    with col1:
        st.image("images/user_icon.png", width=80)
        st.markdown("### 일반회원\n개인 사용자 전용 서비스")
        if st.button("접속하기", key="btn_user"):
            switch_page("auto_mall")

    with col2:
        st.image("images/shop_icon.png", width=80)
        st.markdown("### 딜러 허브\n대리점 및 가맹점 서비스")
        if st.button("접속하기", key="btn_dealer"):
            switch_page("dealer_hub")

    with col3:
        st.image("images/admin_icon.png", width=80)
        st.markdown("### 관리자 콘솔\n운영 및 데이터 관리")
        if st.button("접속하기", key="btn_admin"):
            switch_page("admin_console")

# 다른 페이지 연결
elif st.session_state.current_page == "auto_mall":
    import A_auto_mall as auto
    auto.app()

elif st.session_state.current_page == "dealer_hub":
    import B_dealer_hub as dealer
    dealer.app()

elif st.session_state.current_page == "admin_console":
    import C_admin_console as admin
    admin.app()
