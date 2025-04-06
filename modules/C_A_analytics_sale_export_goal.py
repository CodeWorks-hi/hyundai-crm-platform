# 판매·수출 관리
    # 판매·수출 관리 
        # 해외 판매(수출 관리)수출입 국가별 분석
            # 해외 목표 달성률 집계



# modules/C_A_analytics_sale_export_goal.py

import streamlit as st
import plotly.graph_objects as go
from utils_export import load_and_merge_export_data, get_filter_values

def export_goal_ui():
    st.header("🎯 목표 달성률 분석")
    
    df = load_and_merge_export_data()
    brand, year, country = get_filter_values(df, "goal")
    target = st.number_input("연간 목표량 설정 (대)", min_value=1000, value=100000)
    
    actual = df[(df["브랜드"]==brand)&(df["지역명"]==country)][f"{year}-12"].values[0]
    achievement = (actual / target) * 100

    # 게이지 차트
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=achievement,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [0, 100]}}
    ))
    st.plotly_chart(fig, use_container_width=True)
