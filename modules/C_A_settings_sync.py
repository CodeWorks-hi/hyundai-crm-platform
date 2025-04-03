# 설정 및 환경 관리
    # 데이터 동기화 상태 UI



import streamlit as st

def sync_ui():
    st.subheader("데이터 동기화 상태")

    st.info("데이터 동기화 시스템 상태를 확인하고, 오류 로그 및 마지막 동기화 일시를 확인합니다.")
    st.write("- 마지막 동기화: 2025-03-31 14:22")
    st.success("모든 데이터가 정상적으로 동기화되었습니다.")