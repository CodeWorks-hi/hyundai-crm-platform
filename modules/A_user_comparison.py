# 고객 메인 대시보드     
    # 차량 비교



import streamlit as st
import pandas as pd

def comparison_ui(df_employees, generate_html_table):
    st.subheader(" 차량 비교")
    
    # 예시용 더미 테이블
    sample = pd.DataFrame({
        "트림명": ["모델A", "모델B", "모델C"],
        "연비": [15.2, 14.8, 16.1],
        "가격": [2000, 2200, 2100],
        "출력": [120, 130, 125]
    })

    st.markdown("####  차량 사양 비교표")
    st.markdown(generate_html_table(sample), unsafe_allow_html=True)

