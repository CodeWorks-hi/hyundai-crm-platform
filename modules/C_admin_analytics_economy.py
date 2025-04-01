# 판매·수출 관리
    #  # 글로벌 이코노믹 인텔리전스/# 환율/금리 영향 분석

import streamlit as st

def analytics_economy_ui():
    st.title("글로벌 경제 인사이트")
    st.write("환율, 금리 등 글로벌 경제 지표를 분석하는 페이지입니다.")

    if st.button("← 관리자 포털로 돌아가기"):
        st.switch_page("C_admin_main.py")