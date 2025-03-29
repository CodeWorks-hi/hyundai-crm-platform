# 예: B_dealer_hub.py
import streamlit as st

def app():
    st.title("딜러 허브")
    st.markdown("🏪 가맹점용 판매 및 고객 정보 관리 기능")

    if st.button("← 메인으로 돌아가기"):
        st.session_state.current_page = "home"
        st.rerun()
