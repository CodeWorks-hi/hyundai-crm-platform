# 판매·수출 관리
    # 판매·수출 관리 
        # 국내 판매 (차종/지역별 등)
            # 목표 달성률 집계


import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sb





# CSV 파일 경로
customer_path = "data/customer_data_ready.csv"

# 데이터 로드 함수
@st.cache_data
def load_customer_data(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류 발생: {str(e)}")
        return None

# 국내 판매 UI
def domestic_goal_ui():
    st.subheader("판매·수출 관리")
    st.write("국내 판매 실적을 분석하는 페이지입니다.")
    st.write("차종/지역별 목표 달성률 집계")

    # 데이터 로드
    df = load_customer_data(customer_path)
    if df is None:
        return  # 데이터 로드 실패 시 조기 반환

    # 차량 유형 및 지역별 분석 함수 호출
    vehicle_region_analysis(df)

# 차량 유형 및 지역별 목표 달성률 분석 함수
def vehicle_region_analysis(df):
    vehicle_types = ["전체"] + sorted(df["차량 유형"].unique())
    regions = ["전체"] + sorted(df["거주 지역"].unique())

    # 컬럼 레이아웃
    col1, col2 = st.columns(2)
    with col1:
        selected_vehicle = st.selectbox("차량 유형 선택", vehicle_types, key="vehicle_select")
    with col2:
        selected_region = st.selectbox("지역 선택", regions, key="region_select")

    # 데이터 필터링
    filtered_df = df.copy()
    if selected_vehicle != "전체":
        filtered_df = filtered_df[filtered_df["차량 유형"] == selected_vehicle]
    if selected_region != "전체":
        filtered_df = filtered_df[filtered_df["거주 지역"] == selected_region]

    # 목표값 설정 (예시)
    goal_mapping = {
        ("전체", "전체"): 1000,
        ("SUV", "서울"): 300,
        ("세단", "부산"): 150,
    }
    goal_sales = goal_mapping.get(
        (selected_vehicle, selected_region),
        goal_mapping.get(("전체", "전체"), 100)
    )
    actual_sales = len(filtered_df)
    achievement_rate = round((actual_sales / goal_sales) * 100, 1) if goal_sales > 0 else 0

    if achievement_rate > 100:
        st.warning(f"목표 초과: {actual_sales}/{goal_sales}")
        achievement_rate = 100

    # 차트 생성 (퍼센트 기호 제거)
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=achievement_rate,
        number={'valueformat': ".1f"},  # 퍼센트 기호 제거
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': f"목표 달성률<br><sub>{selected_region} {selected_vehicle}</sub>",
            'font': {'size': 28}
        },
        delta={
            'reference': 100,
            'increasing': {'color': "#2ECC71"},
            'decreasing': {'color': "#E74C3C"},
            'valueformat': ".1f"
        },
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1},
            'bar': {'color': "#3498DB"},
            'steps': [
                {'range': [0, 50], 'color': "#F2D7D5"},
                {'range': [50, 75], 'color': "#D4E6F1"},
                {'range': [75, 100], 'color': "#D5F5E3"}],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.8,
                'value': 100}
        }
    ))

    # 레이아웃 조정
    fig.update_layout(
        margin=dict(l=50, r=50, t=100, b=50),
        height=500
    )
    
    # 가운데 정렬
    col_center = st.columns([1, 3, 1])[1]
    with col_center:
        st.plotly_chart(fig, use_container_width=True)
    
    # 추가 정보 표시 (퍼센트 기호 제거)
    st.subheader("세부 정보")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="목표 판매량", value=f"{goal_sales} 대")
    with col2:
        st.metric(label="실제 판매량", value=f"{actual_sales} 대")
    with col3:
        st.metric(label="목표 달성률", value=f"{achievement_rate}")  # 퍼센트 기호 제거

    # 원본 데이터 보기 옵션 추가
    data_view_option = st.selectbox(
        "데이터 표시 옵션",
        options=["차트만 보기", "원본 데이터 보기"],
        index=0,
        key="vehicle_region_data_view"
    )
    
    if data_view_option == "원본 데이터 보기":
        st.write("전체 데이터 미리보기")
        st.dataframe(df)

# Streamlit 앱 실행
if __name__ == "__main__":
    domestic_goal_ui()
