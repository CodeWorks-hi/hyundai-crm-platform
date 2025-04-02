# 생산·제조 현황 분석



import streamlit as st
from .C_A_production_factory import production_factory_ui
from .C_A_production_trend import production_trend_ui

def production_ui():
    st.subheader("생산·제조 현황 분석")


    tab1, tab2 = st.tabs(["공장별 생산량 비교", "연도별 추이, 목표 달성률"])

    with tab1:
        production_factory_ui()             # 공장별 생산량 비교

    with tab2:
        production_trend_ui()                # 연도별 추이, 목표 달성률
