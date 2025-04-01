# 데이터 동기화 


import streamlit as st

st.set_page_config(page_title="데이터 동기화 상태", layout="wide")
st.title("데이터 동기화 상태")

st.write("시스템 및 데이터의 실시간 동기화 상태를 확인하는 페이지입니다.")

if st.button("← 관리자 포털로 돌아가기"):
    st.switch_page("C_admin_main.py")
