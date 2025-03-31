# 수출입 국가별 분석



import streamlit as st

st.set_page_config(page_title="수출입 국가별 분석", layout="wide")
st.title("🌐 수출입 국가별 분석")

st.write("국가별 수출입 데이터를 분석하고 시각화하는 페이지입니다.")

if st.button("← 관리자 포털로 돌아가기"):
    st.switch_page("C_admin_main.py")
