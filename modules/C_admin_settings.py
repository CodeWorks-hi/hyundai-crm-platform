# 설정 및 환경 관리
# 딜러 성과, KPI 설정, 인센티브 관리



import streamlit as st
from C_admin_settings_users import settings_users_ui

def admin_settings_ui():
    st.title("설정 및 환경 관리")

    st.write("시스템 환경 설정 및 관리 페이지입니다.")

    if st.button("← 관리자 포털로 돌아가기"):
        st.switch_page("C_admin_main.py")
