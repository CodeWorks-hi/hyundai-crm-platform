import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sb
from matplotlib import font_manager, rc
import matplotlib.pyplot as plt
import plotly.express as px
import os
import platform



# 데이터 경로 설정
car_list_path = "data/hyundae_car_list.csv"
inventory_path = "data/inventory_data.csv"
customer_path = "data/customer_data.csv"

# 데이터 로드
df_inv = pd.read_csv(inventory_path)
df_list = pd.read_csv(car_list_path)
df_customer = pd.read_csv(customer_path)

def domestic_performance_ui():

    df_customer['통합 연령대'] = df_customer['연령대'].replace(
            {
                '20대 초반': '20대', '20대 중반': '20대', '20대 후반': '20대',
                '30대 초반': '30대', '30대 중반': '30대', '30대 후반': '30대',
                '40대 초반': '40대', '40대 중반': '40대', '40대 후반': '40대',
                '50대 초반': '50대', '50대 중반': '50대', '50대 후반': '50대',
                '60대 초반': '60대 이상', '60대 중반': '60대 이상', 
                '60대 후반': '60대 이상', '70대 초반': '60대 이상'
            }
        )

    # 선택 연도
    years = sorted(df_customer['최근 구매 연도'].unique())
    default_year = 2024
    if default_year in years:
        default_index = years.index(default_year)
    else:
        default_index = len(years) - 1
    year = st.selectbox(" 연도 선택", years, index=default_index)

    # 데이터 필터링
    df_filtered = df_customer[df_customer['최근 구매 연도'] == year]

    print(df_filtered['최근 구매 연도'])
    # 주요 지표 계산
    total_customers = df_filtered['아이디'].nunique()
    avg_age = df_filtered['현재 나이'].mean()
    total_sales = len(df_filtered)

    # 전년대비 판매 증가율 계산
    if year - 1 in years:
        last_year_sales = len(df_customer[df_customer['최근 구매 연도'] == year - 1])
        YoY_growth = round(((total_sales - last_year_sales) / last_year_sales) * 100, 2) if last_year_sales > 0 else "-"
    else:
        YoY_growth = "-"
        

    # 주요 지표 표시 (카드 스타일)
    st.markdown("###  주요 지표")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 고객 수", f"{total_customers} 명")
    col2.metric("평균 연령", f"{avg_age:.1f} 세")
    col3.metric("전년대비 판매 증가율", f"{YoY_growth}%")
    col4.metric("총 판매량", f"{total_sales} 대")


    # 분포 시각화 (깔끔한 레이아웃)
    st.markdown("---")

    col1_1, col1_2,col3 = st.columns(3)
    with col1_1:
        # Age Selection Dropdown
        age_options = sorted(df_filtered['통합 연령대'].unique().tolist())
        selected_age = st.selectbox("연령대 선택", options=['전체'] + age_options, index=0, key="age_selectbox_1")
    with col1_2:
        # Gender Selection Dropdown
        gender_options = df_filtered['성별'].unique().tolist()
        selected_gender = st.selectbox("성별 선택", options=['전체'] + gender_options, index=0, key="gender_selectbox_1")
    with col3:
        # Grade Selection Dropdown
            grade_options = sorted(df_filtered['고객 그룹'].unique().tolist())
            selected_grade = st.selectbox("등급 선택", options=['전체'] + grade_options, index=0, key="grade_selectbox")

    # 필터링 로직
    filtered_data = df_filtered.copy()

    if selected_age != "전체":
        filtered_data = filtered_data[filtered_data['통합 연령대'] == selected_age]

    if selected_gender != "전체":
        filtered_data = filtered_data[filtered_data['성별'] == selected_gender]

    if selected_grade != "전체":
        filtered_data = filtered_data[filtered_data['고객 그룹'] == selected_grade]

    # 고객 그룹 분포 계산
    grade_counts = filtered_data['고객 그룹'].value_counts()

    # 하단 시각화 영역
    col1, col2 = st.columns(2)

    with col1:
        if grade_counts.empty:
            st.write("필터링된 데이터가 없습니다.")
        else:
            # Plotly 원형 차트 시각화 (고객 그룹 분포)
            fig = px.pie(
                names=grade_counts.index,
                values=grade_counts.values,
                title="고객 분포",
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            # 숫자 표시 제거
            fig.update_traces(textinfo='none')
            
            # 그래프 출력
            st.plotly_chart(fig, use_container_width=True, key="customer_group_chart")

    with col2:
        # 차량 모델 구매 비율 계산
        model_counts = filtered_data['최근 구매 제품'].value_counts()

        if model_counts.empty:
            st.write("필터링된 데이터가 없습니다.")
        else:
            # Plotly 원형 차트 시각화 (차량 모델 구매 비율)
            fig = px.pie(
                names=model_counts.index,
                values=model_counts.values,
                title="차량 분포",
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            # 숫자 표시 제거
            fig.update_traces(textinfo='none')
            
            # 그래프 출력
            st.plotly_chart(fig, use_container_width=True, key="vehicle_model_chart")
    

    st.markdown("---")


    # 구매 트렌드
    st.markdown("### 구매 트렌드")

    # Trend Selection Dropdown
    trend_options = ['분기', '월', '요일', '계절']
    selected_trend = st.selectbox(
        "트렌드 선택", 
        trend_options, 
        index=0,
        key="unique_trend_selectbox"  # Unique key for the dropdown
    )

    # Prepare Trend Data
    if selected_trend == '분기':
        df_filtered['구매 분기'] = pd.to_datetime(df_filtered['최근 구매 날짜']).dt.to_period('Q').astype(str)
        trend_data = df_filtered.groupby('구매 분기')['아이디'].nunique()
    elif selected_trend == '월':
        df_filtered['구매 월'] = pd.to_datetime(df_filtered['최근 구매 날짜']).dt.month
        trend_data = df_filtered.groupby('구매 월')['아이디'].nunique()
    elif selected_trend == '요일':
        days_order = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        trend_data = df_filtered.groupby('구매 요일')['아이디'].nunique().reindex(days_order, fill_value=0)
    elif selected_trend == '계절':
        df_filtered['구매 시즌'] = pd.to_datetime(df_filtered['최근 구매 날짜']).dt.month % 12 // 3 + 1
        season_map = {1: '봄', 2: '여름', 3: '가을', 4: '겨울'}
        df_filtered['구매 시즌'] = df_filtered['구매 시즌'].map(season_map)
        trend_data = df_filtered.groupby('구매 시즌')['아이디'].nunique()

    col1, col2 = st.columns(2)

    with col1:
        # Visualize Data (Line Chart)
        if trend_data.empty:
            st.write("필터링된 데이터가 없습니다.")
        else:
            # Plotly Line Chart Visualization
            fig = px.line(
                x=trend_data.index,
                y=trend_data.values,
                labels={'x': selected_trend, 'y': "구매 고객 수"},
                title=f"{selected_trend}별 구매 트렌드",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Visualize Data (Pie Chart)
        if trend_data.empty:
            st.write("필터링된 데이터가 없습니다.")
        else:
            # Prepare aggregated data for pie chart
            aggregated_data = trend_data.reset_index()  # Convert Series to DataFrame for names and values
            aggregated_data.columns = ['names', 'values']  # Rename columns for Plotly

            # Plotly Pie Chart Visualization
            fig = px.pie(
                names=aggregated_data['names'],
                values=aggregated_data['values'],
                title=f"{selected_trend}별 차량 모델 구매 비율",
                color_discrete_sequence=px.colors.sequential.RdBu
            )

            # 숫자 표시 제거
            fig.update_traces(textinfo='none')
            
            st.plotly_chart(fig, use_container_width=True)


    # 원본데이터 보기
    with st.expander("원본 데이터 보기", expanded=False):
            st.write(df_filtered)

