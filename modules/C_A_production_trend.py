# 생산·제조 현황 분석
    # 연도별 추이, 목표 달성률



import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 데이터 불러오기
car_list_path = "data/hyundae_car_list.csv"
inventory_path = "data/inventory_data.csv"
hyundai_plant_path = "data/processed/total/hyundai-by-plant.csv"

df_list = pd.read_csv(car_list_path)
df_inv = pd.read_csv(inventory_path)
df_plant = pd.read_csv(hyundai_plant_path)

def trend_ui():
    st.title("생산·제조 현황 분석")
    st.markdown("공장별 연도별 생산량 추이 및 목표 달성률을 시각화합니다.")

    # 📌 날짜 컬럼 생성
    df_inv['생산일'] = pd.date_range(start='2022-01-01', periods=len(df_inv), freq='D')
    df_inv['연도'] = pd.to_datetime(df_inv['생산일']).dt.year

    # ✅ 종합 생산 보고서 계산 먼저!
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

        # 🎯 분석 포인트 추출
        max_inv_factory = report.loc[report['총재고량'].idxmax(), '공장명']
        max_rate_factory = report.loc[report['생산효율'].idxmax(), '공장명']
        min_rate_factory = report.loc[report['생산효율'].idxmin(), '공장명']

    # 📊 KPI 시각화
    st.subheader("현대자동차 생산 종합 지표")
    cols = st.columns(4)
    st.markdown("""
        <style>
        .stMetric {padding: 20px; background-color: #f8f9fa; border-radius: 10px;}
        </style>
    """, unsafe_allow_html=True)

    cols[0].metric("총 부품 재고", f"{int(report['총재고량'].sum()):,}개", max_inv_factory)
    cols[1].metric("최대 생산 가능", f"{report['생산가능수량'].max():,}대", report.loc[report['생산가능수량'].idxmax(), '공장명'])
    cols[2].metric("최고 생산 효율", f"{report['생산효율'].max():.2f}%", max_rate_factory)
    cols[3].metric("최저 생산 효율", f"{report['생산효율'].min():.2f}%", min_rate_factory)

    st.markdown("---")

    # 📈 연도별 생산 추이
    trend_df = df_inv.groupby(['연도', '공장명'])['재고량'].sum().reset_index()
    trend_df['목표'] = 10000
    trend_df['달성률 (%)'] = (trend_df['재고량'] / trend_df['목표'] * 100).round(2)

    fig_trend = px.line(
        trend_df,
        x='연도',
        y='재고량',
        color='공장명',
        markers=True,
        title="📈 연도별 공장 생산량 추이"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # 🎯 목표 달성률 바차트
    fig_goal = px.bar(
        trend_df,
        x='공장명',
        y='달성률 (%)',
        color='연도',
        barmode='group',
        title="공장별 연도별 목표 달성률(%)"
    )
    st.plotly_chart(fig_goal, use_container_width=True)

    # 📋 데이터 테이블
    st.subheader("연도별 생산량 및 목표 달성률")
    st.dataframe(trend_df, use_container_width=True)

    # 📁 원본 데이터 확인
    with st.expander("원본 데이터 보기"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("차량 마스터 데이터")
            st.dataframe(df_list, use_container_width=True)
        with col2:
            st.write("부품 재고 데이터")
            st.dataframe(df_inv, use_container_width=True)
