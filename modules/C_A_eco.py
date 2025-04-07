# 탄소 배출량 모니터링
# IGIS 연동 탄소 배출량 모니터링

import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np



# 차량리스트 데이터 불러오기
df_inv = pd.read_csv("data/inventory_data.csv")
df_list = pd.read_csv("data/hyundae_car_list.csv")

np.random.seed(42) 

def load_data():
    for col in ['모델명', '트림명']:
        df_list[col] = df_list[col].astype(str).str.strip()
        df_inv[col] = df_inv[col].astype(str).str.strip()
    df = pd.merge(df_inv, df_list[['모델명', '트림명', '연료구분', 'CO2배출량', '연비']], on=['모델명', '트림명'], how='left')
    # 병합
    df = pd.merge(df_inv, df_list[['모델명', '트림명', '연료구분', 'CO2배출량', '연비']],
                on=['모델명', '트림명'], how='left')

    # 병합 후 사용할 컬럼 정의 (_y 붙은 컬럼 사용)
    df['연료구분'] = df['연료구분_y']
    df['CO2배출량'] = df['CO2배출량_y']
    df['연비'] = df['연비_y']

    # Drop duplicates if needed
    df = df.dropna(subset=['연료구분', 'CO2배출량', '연비', '공장명', '재고량'])
    return df

def load_restriction_data():
    data = {
        "시도": ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "경기도"],
        "단속대상": ["전국 5등급 차량"] * 6,
        "단속제외대상": [
            "저감장치 부착차량, 긴급자동차, 장애인차량, 국가유공자 등",
            "저감장치 부착차량, 영업용 차량, 기초생활수급자, 차상위 계층",
            "저감장치 부착차량, 영업용 차량, 장애인차량, 소상공인",
            "저감장치 부착차량, 국가유공자 등",
            "저감장치 부착차량, 영업용 차량, 소상공인",
            "저감장치 부착 불가 차량 중 기초생활수급자, 소상공인"
        ],
        "과태료": ["1일 10만원"] * 6
    }
    return pd.DataFrame(data)

def eco_ui():
    st.markdown("차량의 연료 구분, CO₂ 배출량, 연비를 기준으로 친환경 수준을 모니터링합니다.")

    df = load_data()
    expected_cols = ["연료구분", "CO2배출량", "연비", "공장명", "재고량"]
    if not all(col in df.columns for col in expected_cols):
        st.error("❌ 데이터 컬럼명이 예상과 다릅니다.")
        st.write("필요한 컬럼:", expected_cols)
        st.write("현재 컬럼:", list(df.columns))
        return

    df = df.dropna(subset=expected_cols).copy()

    # 전기차 vs 내연기관차 분류 및 친환경 점수
    df['전기차 여부'] = df['연료구분'].apply(lambda x: '친환경차' if '전기' in x or '하이브리드' in x else '내연기관차')
    np.random.seed(42)
    df['연도'] = np.random.choice([2020, 2021, 2022, 2023, 2024], size=len(df))
    df['친환경점수'] = df['연비'] * 2 - df['CO2배출량'] * 0.5

    # 공장별 생산량 비교
    eco_summary = df.groupby(['공장명', '전기차 여부'])['재고량'].sum().reset_index()
    fig_eco = px.bar(eco_summary, x='공장명', y='재고량', color='전기차 여부', barmode='group',
                     title='공장별 친환경차 vs 내연기관차 생산량 비교')
    st.plotly_chart(fig_eco, use_container_width=True)

    # 연도별 생산 추이
    trend_summary = df.groupby(['연도', '전기차 여부'])['재고량'].sum().reset_index()
    fig_trend = px.line(trend_summary, x='연도', y='재고량', color='전기차 여부', markers=True,
                        title='연도별 친환경차 vs 내연기관차 생산 추이')
    st.plotly_chart(fig_trend, use_container_width=True)

    # 공장별 친환경 점수 평균
    score_summary = df.groupby('공장명')['친환경점수'].mean().reset_index()
    fig_score = px.bar(score_summary, x='공장명', y='친환경점수', color='친환경점수', color_continuous_scale='Greens',
                       title='공장별 평균 친환경 점수')
    st.plotly_chart(fig_score, use_container_width=True)

    st.markdown("---")
    st.subheader("🚫 계절관리제 운행제외 대상 정보")
    restriction_df = load_restriction_data()
    st.dataframe(restriction_df, use_container_width=True, hide_index=True)

    # 🗂 원본 데이터 섹션
    with st.expander("🗂 원본 데이터 확인", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write("차량 마스터 데이터")
            st.dataframe(df_list, use_container_width=True, hide_index=True)
        with col2:
            st.write("부품 재고 데이터")
            st.dataframe(df_inv, use_container_width=True, hide_index=True)
