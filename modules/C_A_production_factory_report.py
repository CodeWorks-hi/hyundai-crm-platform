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
    try:
        df_inv = pd.read_csv("data/inventory_data.csv")
        df_list = pd.read_csv("data/hyundae_car_list.csv")
        
        # 데이터 정제
        df_inv['트림명'] = df_inv['트림명'].astype(str).str.strip()
        df_list['트림명'] = df_list['트림명'].astype(str).str.strip()
        return df_inv, df_list
    except FileNotFoundError as e:
        st.error(f"파일을 찾을 수 없습니다: {str(e)}")
        st.stop()


# 생산 분석 리포트 UI 함수
def report_ui(df_inv):
    with st.spinner("생산 분석 데이터 처리 중..."):
        # 생산 가능 수량 계산
        total_prod = prod_capacity.groupby('공장명').sum().reset_index(name='생산가능수량')
        prod_capacity = df_inv.groupby(['공장명', '모델명', '트림명'])['재고량'].min().reset_index()
        prod_capacity.rename(columns={'재고량': '생산가능수량'}, inplace=True)

        # 2. 계층별 집계
        factory_cap = prod_capacity.groupby('공장명')['생산가능수량'].sum().reset_index()
        model_cap = prod_capacity.groupby('모델명')['생산가능수량'].sum().reset_index()
        trim_cap = prod_capacity.groupby(['모델명','트림명'])['생산가능수량'].sum().reset_index()

        # 재고 분석
        inventory_analysis = df_inv.groupby('공장명').agg(
            총재고량=('재고량', 'sum'),
            평균재고=('재고량', 'mean'),
            고유부품수=('부품명', 'nunique')
        ).reset_index()

        # 종합 리포트 생성
        report = pd.merge(total_prod, inventory_analysis, on='공장명')
        report['생산효율'] = (report['생산가능수량'] / report['총재고량'] * 100).round(2)

        report = report.astype({
            '생산가능수량': 'int',
            '총재고량': 'int',
            '고유부품수': 'int'
        })

    col1, col2 = st.columns(2)
    # 시각화
    with col1:
        st.subheader("공장별 생산능력 및 재고량 비교", divider="blue")
        fig = px.bar(
            report.sort_values('생산가능수량', ascending=False),
            x='공장명', 
            y=['생산가능수량', '총재고량'],
            labels={'value': '수량', 'variable': '구분'},
            barmode='group',
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
            st.subheader("공장별 생산효율 분포", divider="green")
            fig2 = px.scatter(
                report,
                x='총재고량',
                y='생산효율',
                size='고유부품수',
                color='공장명',
                hover_data=['평균재고'],
                title="재고량 대비 생산효율",
                height=600
            )
            fig2.update_traces(marker=dict(size=14))
            st.plotly_chart(fig2, use_container_width=True)

            