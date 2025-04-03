# 판매·수출 관리
    # 판매·수출 관리 
        # 해외 판매(수출 관리)수출입 국가별 분석


import streamlit as st
from .C_A_analytics_sale_export_performance import export_performance_ui
from .C_A_analytics_sale_export_region import export_region_ui
from .C_A_analytics_sale_export_goal import export_goal_ui
from .C_A_analytics_sale_export_growth import export_growth_ui

def export_ui():

    # 탭 구성
    tab1, tab2, tab3, tab4= st.tabs([
          "수출실적","국가별 비교", "목표 달성률", "성장률 분석"
    ])


    with tab1:
        export_performance_ui()
    with tab2:
        export_region_ui()
    with tab3:
        export_goal_ui()
    with tab4:
        export_growth_ui()


