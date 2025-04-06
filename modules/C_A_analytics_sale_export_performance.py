# 판매·수출 관리
    # 판매·수출 관리 
        # 해외 판매(수출 관리)수출입 국가별 분석
            # 해외 실적 분석



# modules/C_A_analytics_sale_export_performance.py

import streamlit as st
import pandas as pd
import plotly.express as px
from .utils_export import load_and_merge_export_data, get_filter_values

def export_performance_ui():
    st.header("🌍 수출 실적 대시보드")
    
    df = load_and_merge_export_data()
    if df is None:
        st.error("데이터 로드 실패")
        return

    brand, year, country = get_filter_values(df, "performance")
    month_cols = [col for col in df.columns if col.startswith(str(year))]
    
    filtered = df[(df["브랜드"] == brand) & (df["지역명"] == country)]
    
    if not filtered.empty:
        # 실적 요약
        col1, col2, col3 = st.columns(3)
        total = filtered[month_cols].sum().sum()
        col1.metric("총 수출량", f"{total:,} 대")
        col2.metric("평균 월별", f"{total/len(month_cols):,.0f} 대")
        col3.metric("차종 수", filtered["차량 구분"].nunique())

        # 시계열 차트
        fig = px.line(
            filtered.melt(id_vars=["차량 구분"], value_vars=month_cols, 
                        var_name="월", value_name="수출량"),
            x="월", y="수출량", color="차량 구분",
            title=f"{year}년 {brand} {country} 수출 추이"
        )
        st.plotly_chart(fig, use_container_width=True)

