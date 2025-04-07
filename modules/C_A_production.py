# 생산·제조 현황 분석



import streamlit as st
from .C_A_production_factory import factory_ui
from .C_A_production_trend import trend_ui

def production_ui():


    tab1, tab2 = st.tabs(["공장별 생산량 비교", "연도별 추이, 목표 달성률"])

    with tab1:
        factory_ui()             # 공장별 생산량 비교

    with tab2:
        trend_ui()                # 연도별 추이, 목표 달성률
