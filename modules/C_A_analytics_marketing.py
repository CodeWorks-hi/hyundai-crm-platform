# 판매·수출 관리
    # 마케팅 캠페인/ # 캠페인 성과 측정

import streamlit as st
from .C_A_analytics_marketing_strategies import strategies_ui
from .C_A_analytics_marketing_campaign import campaign_ui
from modules.C_A_analytics_marketing_campaigns import render_campaign_register, render_campaign_manager


def marketing_ui():
    tab1, tab2, tab3 = st.tabs(["마케팅 전략", "캠폐인 분석", "캠폐인 관리"])

    with tab1:
        strategies_ui()  

    with tab2:
        campaign_ui()  

    with tab3:
        col1, col2 = st.columns([1,1])
        with col1:
            render_campaign_register()
        st.markdown("---")
        with col2:
            render_campaign_manager()



    