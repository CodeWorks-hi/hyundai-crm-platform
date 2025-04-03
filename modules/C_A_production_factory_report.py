# 생산·제조 현황 분석
    # 현대자동차 생산 현황 실시간 모니터링 시스템
        # 생산 분석 리포트 생성 함수


import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np


# 데이터 로드 함수
@st.cache_data
def load_data():
    df_inv = pd.read_csv("data/inventory_data.csv")
    df_list = pd.read_csv("data/hyundae_car_list.csv")

    # 데이터 정제
    df_inv['트림명'] = df_inv['트림명'].astype(str).str.strip()
    df_list['트림명'] = df_list['트림명'].astype(str).str.strip()
    return df_inv, df_list

# 생산 분석 리포트 생성 함수
def report_ui(df_inv):
    with st.spinner("생산 분석 데이터 처리 중..."):
        prod_capacity = df_inv.groupby(['공장명', '모델명', '트림명'])['재고량'].min()
        total_prod = prod_capacity.groupby('공장명').sum().reset_index(name='생산가능수량')

        inventory_analysis = df_inv.groupby('공장명').agg(
            총재고량=('재고량', 'sum'),
            평균재고=('재고량', 'mean'),
            고유부품수=('부품명', 'nunique')
        ).reset_index()

        report = pd.merge(total_prod, inventory_analysis, on='공장명')
        report['생산효율'] = (report['생산가능수량'] / report['총재고량'] * 100).round(2)

        report = report.astype({
            '생산가능수량': 'int',
            '총재고량': 'int',
            '고유부품수': 'int'
        })
        return report
    
    st.title("현대자동차 생산 현황 실시간 모니터링 시스템")
    cols = st.columns(4)
    st.markdown("""<style>.stMetric {padding: 20px; background-color: #f8f9fa; border-radius: 10px;}</style>""", unsafe_allow_html=True)

    cols[0].metric("총 부품 재고", f"{int(factory_report['총재고량'].sum()) :,}개", help="전체 공장의 부품 재고 총합")
    cols[1].metric("최대 생산 가능", f"{int(factory_report['생산가능수량'].max()) :,}대", factory_report.loc[factory_report['생산가능수량'].idxmax(), '공장명'])
    cols[2].metric("최고 생산 효율", f"{float(factory_report['생산효율'].max()):.2f}%", factory_report.loc[factory_report['생산효율'].idxmax(), '공장명'])
    cols[3].metric("평균 회전율", f"{float(factory_report['생산효율'].mean()):.1f}%", help="전체 공장의 평균 재고 회전율")