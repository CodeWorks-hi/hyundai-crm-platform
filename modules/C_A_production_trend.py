# 생산·제조 현황 분석
    # 연도별 추이, 목표 달성률



import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 데이터 불러오기

# 차량리스트 데이터 불러오기
car_list_path = "data/hyundae_car_list.csv"
df_list = pd.read_csv(car_list_path)

# 부품 재고 데이터 불러오기
inventory_path = "data/inventory_data.csv"
df_inv = pd.read_csv(inventory_path)




def trend_ui():

    # 임의로 날짜 생성 (생산일자가 없다면)
    df_inv['생산일'] = pd.date_range(start='2022-01-01', periods=len(df_inv), freq='D')
    df_inv['연도'] = pd.to_datetime(df_inv['생산일']).dt.year

    # 연도별 공장 생산량 요약
    trend_df = df_inv.groupby(['연도', '공장명'])['재고량'].sum().reset_index()

    #  연도별 생산 추이 라인차트
    fig_trend = px.line(trend_df,
                        x='연도',
                        y='재고량',
                        color='공장명',
                        markers=True,
                        title="연도별 공장 생산량 추이",
                        labels={'연도': '연도', '재고량': '총 생산량'})

    st.plotly_chart(fig_trend, use_container_width=True)

    #  목표 달성률 계산
    trend_df['목표'] = 10000  # 모든 공장 동일 목표 설정
    trend_df['달성률 (%)'] = (trend_df['재고량'] / trend_df['목표']) * 100

    # 바차트로 달성률 비교
    fig_goal = px.bar(trend_df,
                    x='공장명',
                    y='달성률 (%)',
                    color='연도',
                    barmode='group',
                    title="공장별 연도별 목표 달성률(%)")

    st.plotly_chart(fig_goal, use_container_width=True)

    #  데이터 테이블 제공
    st.subheader(" 연도별 생산량 및 목표 달성률")
    st.dataframe(trend_df)

    # 원본 데이터 섹션
    with st.expander("📁 원본 데이터 확인", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write("차량 마스터 데이터")
            st.dataframe(df_list, use_container_width=True)
        with col2:
            st.write("부품 재고 데이터")
            st.dataframe(df_inv, use_container_width=True)
