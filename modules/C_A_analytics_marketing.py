# 판매·수출 관리
    # 마케팅 캠페인/ # 캠페인 성과 측정

import streamlit as st
from .C_A_analytics_marketing_strategies import strategies_ui
from .C_A_analytics_marketing_campaign import campaign_ui

def marketing_ui():
    tab1, tab2= st.tabs(["마케팅 전략", "캠페인 관리 메뉴"])

    with tab1:
        strategies_ui()  

    with tab2:
        campaign_ui()  


    