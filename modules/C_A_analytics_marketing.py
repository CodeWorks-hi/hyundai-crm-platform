# 판매·수출 관리
    # 마케팅 캠페인/ # 캠페인 성과 측정

import streamlit as st
from .C_A_analytics_marketing_strategies import marketing_strategies_ui
from .C_A_analytics_marketing_campaign import marketing_campaign_ui
from .C_A_analytics_economy_realtime import marketing_realtime_ui

def analytics_marketing_ui():
    tab1, tab2= st.tabs(["마케팅 전략", "캠페인 관리 메뉴"])

    with tab1:
        marketing_strategies_ui()  

    with tab2:
        marketing_campaign_ui()  


    