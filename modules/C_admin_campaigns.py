# 마케팅 캠페인



import streamlit as st

st.set_page_config(page_title="마케팅 캠페인 관리", layout="wide")
st.title("📈 마케팅 캠페인 관리")

st.write("마케팅 캠페인의 성과 분석 및 관리 페이지입니다.")

if st.button("← 관리자 포털로 돌아가기"):
    st.switch_page("C_admin_main.py")