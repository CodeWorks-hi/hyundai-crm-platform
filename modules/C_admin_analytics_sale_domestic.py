# 판매·수출 관리
    # 판매·수출 관리 
        # 국내 판매 (차종/지역별 등)



import pandas as pd
import streamlit as st

def analytics_domestic_ui():

    st.write("현대/기아의 국내 판매 실적을 분석하는 페이지입니다.")

    df = pd.read_csv("data/domestic_sales.csv")
    st.dataframe(df)

    st.write("국내 판매 실적을 분석한 결과입니다.")


