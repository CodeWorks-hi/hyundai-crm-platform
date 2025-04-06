# 판매·수출 관리
    # 판매·수출 관리 
        # 해외 판매(수출 관리)수출입 국가별 분석
            # 해외 성장률 트렌드 분석



# modules/C_A_analytics_sale_export_growth.py

import streamlit as st
import pandas as pd
import altair as alt
from .utils_export import load_and_merge_export_data

def export_growth_ui():
    st.header("📈 성장률 트렌드 분석")
    
    df = load_and_merge_export_data()
    brand = st.selectbox("분석 대상 브랜드", df["브랜드"].unique())
    
    if brand:
        growth_data = df[df["브랜드"]==brand].groupby("연도").sum().pct_change()*100
        
        chart = alt.Chart(growth_data.reset_index()).mark_area().encode(
            x='연도:O',
            y='증가율:Q',
            tooltip=['연도', alt.Tooltip('증가율', format='.2f')]
        )
        st.altair_chart(chart, use_container_width=True)
