# modules/utils_export.py

import pandas as pd
import streamlit as st
import re

@st.cache_data
def load_and_merge_export_data():
    """검색 결과 [1]의 IGIS 아키텍처 반영"""
    df = pd.read_csv("data/export_customer_data.csv")
    
    # 컬럼명 영어 변환 (검색 결과의 데이터 모델 반영)
    column_mapping = {
        '연번': 'id',
        '거주 지역': 'region',
        '고객 등급': 'customer_grade',
        '최근 구매 제품': 'last_purchased_model'
    }
    df = df.rename(columns=column_mapping)
    
    # 브랜드 추출 로직 (검색 결과의 제품명 규칙 반영)
    df['brand'] = df['last_purchased_model'].apply(
        lambda x: re.split(r'\d+', x)[0].strip() if pd.notnull(x) else 'unknown'
    )
    
    return df

def get_filter_values(df, prefix):
    """검색 결과 [1]의 UI 가이드라인 반영"""
    cols = st.columns(3)
    filters = {}
    with cols[0]:
        filters['region'] = st.selectbox(
            "지역 선택", 
            df['region'].unique(), 
            key=f"{prefix}_region"
        )
    with cols[1]:
        filters['year'] = st.selectbox(
            "연도 선택",
            sorted(df['최근 구매 연도'].unique()),
            key=f"{prefix}_year"
        )
    with cols[2]:
        filters['brand'] = st.selectbox(
            "브랜드 선택",
            df['brand'].unique(),
            key=f"{prefix}_brand"
        )
    return filters
