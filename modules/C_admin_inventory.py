# 재고 자동 경고 


import streamlit as st

st.set_page_config(page_title="재고 자동 경고", layout="wide")
st.title("⚠️ 재고 자동 경고")

st.write("재고 수준을 모니터링하고 자동으로 경고하는 페이지입니다.")

if st.button("← 관리자 포털로 돌아가기"):
    st.switch_page("C_admin_main.py")
