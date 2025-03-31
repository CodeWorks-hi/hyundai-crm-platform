# 설정 및 환경 관리



import streamlit as st

st.set_page_config(page_title="설정 및 환경 관리", layout="wide")
st.title("⚙️ 설정 및 환경 관리")

st.write("시스템 환경 설정 및 관리 페이지입니다.")

if st.button("← 관리자 포털로 돌아가기"):
    st.switch_page("C_admin_main.py")
