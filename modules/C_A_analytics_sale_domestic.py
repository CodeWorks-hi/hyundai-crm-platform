# 판매·수출 관리
    # 판매·수출 관리 
        # 국내 판매 (차종/지역별 등)



import pandas as pd
import streamlit as st
<<<<<<< HEAD
import matplotlib.pyplot as plt 
import seaborn as sb
=======
from .C_A_analytics_sale_domestic_performance import domestic_performance_ui
from .C_A_analytics_sale_domestic_region import domestic_region_ui
from .C_A_analytics_sale_domestic_goal import domestic_goal_ui
from .C_A_analytics_sale_domestic_growth import domestic_growth_ui
>>>>>>> f73ec2108e4182671d8f0dc09f63a8d262cab53b

def domestic_ui():

    # 탭 구성
    tab1, tab2, tab3, tab4= st.tabs([
          "국내실적","지역별 비교", "목표 달성률", "성장률 분석"
    ])

<<<<<<< HEAD
    
=======
    with tab1:
       domestic_performance_ui()
    with tab2:
        domestic_region_ui()
    with tab3:
        domestic_goal_ui()
    with tab4:
       domestic_growth_ui()





>>>>>>> f73ec2108e4182671d8f0dc09f63a8d262cab53b
