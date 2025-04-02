# 판매·수출 관리
    # 판매·수출 관리 
        # 국내 판매 (차종/지역별 등)



import pandas as pd
import streamlit as st

def domestic_ui():

    # 탭 구성
    tab1, tab2, tab3, tab4= st.tabs([
          "국내실적","지역별 비교", "목표 달성률", "성장률 분석"
    ])



