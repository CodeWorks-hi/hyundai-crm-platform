# 판매·수출 관리
    # 판매·수출 관리 - 국내/해외 실적 분석 대시보드 코드 템플릿 생성
    # 판매·수출 데이터 분석 대시보드
    # 목표 달성률, 성장률 분석
    # 시각화 대시보드




import streamlit as st
from .C_A_analytics_sale_domestic import domestic_ui
from .C_A_analytics_sale_export import export_ui

def analytics_sales_ui():

    tab1, tab2 = st.tabs([
        "국내 판매 실적", 
        "해외 수출입 실적"
    ])

    with tab1:
        domestic_ui()

    with tab2:
        export_ui()


