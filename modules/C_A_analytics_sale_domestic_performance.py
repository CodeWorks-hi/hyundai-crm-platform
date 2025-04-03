# 판매·수출 관리
    # 판매·수출 관리 
        # 국내 판매 (차종/지역별 등)
            # 국내 실적 분석



import streamlit as st
import pandas as pd


car_list_path = "data/hyundae_car_list.csv"
inventory_path = "data/inventory_data.csv"
customer_path = "data/customer_data.csv"

df_inv = pd.read_csv(inventory_path)
df_list = pd.read_csv(car_list_path)
df_customer = pd.read_csv(customer_path)

def domestic_performance_ui():
    st.subheader(" 국내 실적 요약")
    st.write("고객의 전체 구매 실적 및 기본 통계 정보를 표시합니다.")
