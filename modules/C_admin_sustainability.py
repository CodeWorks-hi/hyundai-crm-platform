# 탄소 배출량 모니터링



import streamlit as st

st.set_page_config(page_title="탄소 배출량 모니터링", layout="wide")
st.title("🌿 탄소 배출량 모니터링")

st.write("차량 수명 주기 전체에 대한 탄소 배출량을 분석하는 페이지입니다.")

if st.button("← 관리자 포털로 돌아가기"):
    st.switch_page("C_admin_main.py")
