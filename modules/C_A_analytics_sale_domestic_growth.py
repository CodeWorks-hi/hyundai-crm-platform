# 판매·수출 관리
    # 판매·수출 관리 
        # 국내 판매 (차종/지역별 등)
            # 성장률 트렌드 분석


import streamlit as st
import pandas as pd
import plotly.express as px

customer_path = "data/domestic_customer_data.csv"
df_customer = pd.read_csv(customer_path)


def domestic_growth_ui():
    col1,col2,col3=st.columns(3)
    with col1:
        years = sorted(df_customer['구매연도'].unique())
        selected_year = st.selectbox("연도 선택", years)

    with col2:
        regions = ['전체'] + sorted(df_customer['거주 지역'].unique())  # '전체' 옵션 추가
        selected_region = st.selectbox("지역 선택", regions)

    with col3:
        categorys = ['전체'] + sorted(df_customer['모델명'].unique())  # '전체' 옵션 추가
        selected_category = st.selectbox("차종 선택", categorys)


    # 필터링 로직
    filtered_data = df_customer[df_customer['구매연도'] == selected_year]  # 선택한 연도로 필터링

    if selected_region != '전체':
        filtered_data = filtered_data[filtered_data['거주 지역'] == selected_region]

    if selected_category != '전체':
        filtered_data = filtered_data[filtered_data['모델명'] == selected_category]

    # 월별 구매량 계산
    monthly_trend_data = filtered_data.groupby('구매월')['연락처'].count()

    # 성장률 계산
    monthly_growth_rate = monthly_trend_data.pct_change().fillna(0) * 100

    # 시각화 데이터 준비
    if monthly_growth_rate.empty:
        st.write("필터링된 데이터가 없습니다.")
    else:
        
        # Plotly 라인 차트 시각화
        fig = px.line(
            x=monthly_growth_rate.index,
            y=monthly_growth_rate.values,
            labels={'x': "월", 'y': "성장률 (%)"},
            title=f"{selected_year}년 {selected_region} 지역 {selected_category} 월별 성장률",
            markers=True
        )
        
        st.plotly_chart(fig, use_container_width=True)