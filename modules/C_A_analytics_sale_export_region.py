# 판매·수출 관리
    # 판매·수출 관리 
        # 해외 판매(수출 관리)수출입 국가별 분석
            # 해외  시장 비교



# modules/C_A_analytics_sale_export_region.py

import streamlit as st
import pandas as pd
import plotly.express as px
from utils_export import load_and_merge_export_data

def export_region_ui():
    st.header("🗺️ 국가별 시장 비교 분석")
    
    df = load_and_merge_export_data()
    brand = st.selectbox("브랜드 선택", df["브랜드"].unique())
    
    if brand:
        region_data = df[df["브랜드"] == brand].groupby("지역명").sum(numeric_only=True).reset_index()
        
        fig = px.treemap(
            region_data,
            path=['지역명'],
            values='2025-12',  # 최신 월 데이터
            color='지역명',
            title=f"{brand} 국가별 시장 점유율"
        )
        st.plotly_chart(fig, use_container_width=True)


