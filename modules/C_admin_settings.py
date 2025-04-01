# 설정 및 환경 관리
# 딜러 성과, KPI 설정, 인센티브 관리


import streamlit as st
from .C_admin_settings_users import settings_users_ui
from .C_admin_settings_sync import settings_sync_ui

def admin_settings_ui():
    st.subheader(" 설정 및 환경 관리")

    tab1, tab2 = st.tabs(["사용자 관리", "데이터 동기화 상태"])

    with tab1:
        settings_users_ui()

    with tab2:
        settings_sync_ui()