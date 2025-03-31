# 생산·제조 현황 분석



import streamlit as st

st.set_page_config(page_title="생산·제조 현황 분석", layout="wide")
st.title("🏭 생산·제조 현황 분석")

st.write("생산 및 제조 현황을 분석하는 페이지입니다.")

if st.button("← 관리자 포털로 돌아가기"):
    st.switch_page("C_admin_main.py")
