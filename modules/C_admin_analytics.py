# 판매·수출 모니터링 


import streamlit as st

st.set_page_config(page_title="판매·수출 모니터링", layout="wide")
st.title("📊 판매·수출 모니터링")

st.write("판매 및 수출 데이터를 시각화 및 분석하는 페이지입니다.")

if st.button("← 관리자 포털로 돌아가기"):
    st.switch_page("C_admin_main.py")