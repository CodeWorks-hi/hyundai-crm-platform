# modules/utils_export.py

import pandas as pd
import streamlit as st
import re

@st.cache_data
def load_and_merge_export_data():
    # 실제 데이터 로드 구현
    return pd.read_csv("data/export_customer_data.csv")

def get_filter_values(df, prefix):
    col1, col2, col3 = st.columns(3)
    with col1:
        brand = st.selectbox("브랜드", df["브랜드"].unique(), key=f"{prefix}_brand")
    with col2:
        year = st.selectbox("연도", sorted(df["연도"].unique()), key=f"{prefix}_year")
    with col3:
        country = st.selectbox("국가", df["지역명"].unique(), key=f"{prefix}_country")
    return brand, year, country
