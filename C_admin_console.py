# 예: C_admin_console.py
import streamlit as st

def app():
    st.title("관리자 콘솔")
    tabs = st.tabs(["데이터 관리", "운영 통계", "사용자 관리"])

    with tabs[0]:
        st.write("판매, 생산, 수출 데이터 업로드 및 삭제")

    with tabs[1]:
        st.write("운영 지표 시각화")

    with tabs[2]:
        st.write("회원 목록 및 권한 관리")

    if st.button("← 메인으로 돌아가기"):
        st.session_state.current_page = "home"
        st.rerun()
