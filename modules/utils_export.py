# modules/utils_export.py

import pandas as pd
import streamlit as st
import re

@st.cache_data
def load_and_merge_export_data():
    """수출 고객 데이터 로드 및 전처리 함수"""
    df = pd.read_csv("data/export_customer_data.csv")
    
    # 컬럼명 영어 변환
    df = df.rename(columns={
        '연번': 'serial',
        '거주 지역': 'region',
        '최근 구매 연도': 'purchase_year',
        '고객 등급': 'customer_grade',
        '누적 구매 금액': 'total_purchase'
    })
    
    # 브랜드 정보 추출 (제품명에서 추출)
    df['brand'] = df['최근 구매 제품'].apply(lambda x: re.split(r'\d+', x)[0].strip())
    
    return df

def get_filter_values(df, prefix):
    """필터 설정 컴포넌트"""
    col1, col2, col3 = st.columns(3)
    with col1:
        region = st.selectbox("지역", df["region"].unique(), key=f"{prefix}_region")
    with col2:
        year = st.selectbox("구매연도", sorted(df["purchase_year"].unique()), key=f"{prefix}_year")
    with col3:
        brand = st.selectbox("브랜드", df["brand"].unique(), key=f"{prefix}_brand")
    return region, year, brand
