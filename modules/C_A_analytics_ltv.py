# 판매·수출 관리
    # LTV 모델 결과, 시장 트렌드, 예측 분석


# C_A_analytics_ltv_main.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import joblib
from datetime import datetime, timedelta
from .C_A_analytics_ltv_demand import ltv_demand_ui
from .C_A_analytics_ltv_market import ltv_market_ui
from .C_A_analytics_ltv_customer import ltv_customer_ui



# 메인 레이아웃
def ltv_ui():
    
    tab1, tab2, tab3 = st.tabs([
        " 수요 및 발주 예측", 
        " 시장 트렌드", 
        " LTV(고객생애가치) 분석"
    ])
    
    with tab1:
        ltv_demand_ui()
        
    with tab2:
        ltv_market_ui()
        
    with tab3:
        ltv_customer_ui()

