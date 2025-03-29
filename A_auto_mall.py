# A_auto_mall.py

import streamlit as st

def app():
    st.title("오토몰 사용자 페이지")
    st.markdown("🚗 차량 구매, 등록, 조회 등의 기능 제공")

    if st.button("← 메인으로 돌아가기"):
        st.session_state.current_page = "home"
        st.rerun()
