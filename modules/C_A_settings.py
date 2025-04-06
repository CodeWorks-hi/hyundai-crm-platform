# 사용자 및 환경 관리
# 딜러 성과, KPI 설정, 인센티브 관리


import streamlit as st
from .C_A_settings_users import users_ui
from .C_A_settings_sync import sync_ui

def settings_ui():
    tab1, tab2 = st.tabs(["사용자 관리", "데이터 동기화 상태"])

    with tab1:
        users_ui()

    with tab2:
        sync_ui()