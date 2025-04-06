# 판매·수출 관리
    # 마케팅 캠페인/ # 캠페인 성과 측정
        #  캠페인 관리 메뉴



import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from kafka import KafkaConsumer
import json
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import math

# 데이터 경로 설정
real_path = "extra_data/processed/경제 성장 관련/GDP_GNI_real.csv"
nom_path = "extra_data/processed/경제 성장 관련/GDP_GNI_nom.csv"
sen_path = "extra_data/processed/소비 심리 관련/econ_senti_index.csv"
news_path = "extra_data/processed/소비 심리 관련/news_senti_index.csv"
list_path = "data/customers.csv"
event_path = "data/event.csv"

@st.cache_data
def load_data():
    df_real = pd.read_csv(real_path)
    df_nom = pd.read_csv(nom_path)
    df_sen = pd.read_csv(sen_path)
    df_news = pd.read_csv(news_path)
    df_list = pd.read_csv(list_path)
    df_event = pd.read_csv(event_path)
    return df_real, df_nom, df_sen, df_news, df_list, df_event

def render_paginated_list(df, category_name, current_page_key):
    items_per_page = 5
    df = df[df["구분"] == category_name].sort_values(by="등록일", ascending=False).reset_index(drop=True)
    total_pages = math.ceil(len(df) / items_per_page)
    current_page = st.session_state.get(current_page_key, 1)

    start = (current_page - 1) * items_per_page
    end = start + items_per_page
    paginated_df = df.iloc[start:end]

    for _, row in paginated_df.iterrows():
        with st.expander(row["제목"]):
            st.markdown(row["내용"])

    if total_pages > 1:
        cols = st.columns(total_pages + 2)
        with cols[0]:
            if st.button("◀", key=f"{category_name}_prev") and current_page > 1:
                st.session_state[current_page_key] = current_page - 1
                st.rerun()
        for i in range(total_pages):
            with cols[i + 1]:
                if st.button(str(i + 1), key=f"{category_name}_page_{i+1}"):
                    st.session_state[current_page_key] = i + 1
                    st.rerun()
        with cols[-1]:
            if st.button("▶", key=f"{category_name}_next") and current_page < total_pages:
                st.session_state[current_page_key] = current_page + 1
                st.rerun()

# 한글 폰트 설정 (윈도우/Mac/Linux 공통 지원)
def set_korean_font():
    try:
        # 맥OS
        plt.rcParams['font.family'] = 'AppleGothic'
    except:
        try:
            # 윈도우
            plt.rcParams['font.family'] = 'Malgun Gothic'
        except:
            # 리눅스 (나눔고딕 또는 기본)
            plt.rcParams['font.family'] = 'NanumGothic'
    plt.rcParams['axes.unicode_minus'] = False

set_korean_font()


def campaign_ui():
    st.markdown("""
    ##  마케팅 캠페인 성과 분석

    ### 💡 인사이트 요약
    - 최근 **소비자 심리지수 회복** → 고관여 제품 관심도 증가
    - **금리/환율 안정기** 진입 → 금융 캠페인 효율성 상승
    - **보상판매, 리타겟팅 캠페인 응답률** 눈에 띄게 상승
    """)

    # 캠페인별 응답률 예시 데이터
    campaign_data = pd.DataFrame({
        "캠페인명": ["전기차 시승권 제공", "보상판매 리타겟팅", "무이자 금융 프로모션", "SUV 비교체험단"],
        "응답률(%)": [12.5, 8.3, 10.2, 7.1],
        "전환율(%)": [5.4, 3.9, 4.6, 3.2],
        "ROI": [2.8, 1.9, 2.3, 1.7]
    })

    # 응답률 & 전환율 바차트
    st.subheader(" 캠페인별 응답률 & 전환율")
    fig = px.bar(campaign_data, x="캠페인명", y=["응답률(%)", "전환율(%)"],
                 barmode="group", color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)

    #  ROI 추이
    st.subheader(" ROI 추이")
    fig2 = px.line(campaign_data, x="캠페인명", y="ROI", markers=True)
    st.plotly_chart(fig2, use_container_width=True)

    # 👉 추천 액션
    st.markdown("####  추천 액션")
    st.markdown("""
    - `응답률 10% 이상 캠페인` 중심으로 **예산 재배분**
    - `ROI 2.0 이상` 캠페인은 **전국 확대 검토**
    - `전기차·SUV 세그먼트` → 시승 기반 프로모션 지속 필요
    """)

    # 📉 뉴스심리지수 vs 응답률 (시계열 비교)
    st.subheader(" 뉴스심리지수 vs 캠페인 응답률 추이")

    dates = pd.date_range(start="2023-01-01", periods=12, freq="MS")
    news_sentiment = pd.Series([95, 90, 88, 92, 97, 85, 82, 78, 80, 87, 91, 94], index=dates, name="뉴스심리지수")
    response_rate = pd.Series([4.2, 4.0, 3.8, 4.1, 4.6, 3.5, 3.3, 3.1, 3.2, 3.8, 4.0, 4.3], index=dates, name="응답률 (%)")

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.set_title("뉴스심리지수 vs 마케팅 캠페인 응답률", fontsize=16)
    ax1.set_xlabel("월", fontsize=12)
    ax1.set_ylabel("뉴스심리지수", color="blue")
    ax1.plot(news_sentiment.index, news_sentiment.values, color="blue", marker='o', label="뉴스심리지수")
    ax1.tick_params(axis='y', labelcolor="blue")

    ax2 = ax1.twinx()
    ax2.set_ylabel("응답률 (%)", color="green")
    ax2.plot(response_rate.index, response_rate.values, color="green", linestyle='--', marker='s', label="응답률")
    ax2.tick_params(axis='y', labelcolor="green")

    plt.grid(True)
    plt.tight_layout()
    st.pyplot(fig)
    # GDP 실질 성장률 시각화
    st.markdown(" #### 국내총생산(GDP) 실질 추이")
    df_gdp = df_real[df_real["계정항목"] == "국내총생산(시장가격, GDP)"].copy()
    df_gdp = df_gdp.set_index("계정항목").T
    df_gdp.columns = ["GDP"]
    df_gdp = df_gdp.applymap(lambda x: float(str(x).replace(",", "")))
    df_gdp["분기"] = df_gdp.index
    fig_gdp = px.line(df_gdp, x="분기", y="GDP", title="국내총생산(GDP) 실질 추이", markers=True)
    st.plotly_chart(fig_gdp, use_container_width=True)

    # 소비자심리지수 vs 마케팅 반응률
    st.markdown(" #### 소비자심리지수 vs 마케팅 반응률")
    dates = pd.date_range(start="2022-01-01", periods=24, freq="M")
    consumer_sentiment = np.random.normal(loc=90, scale=5, size=len(dates))
    response_rate = 5 + (consumer_sentiment - np.mean(consumer_sentiment)) * 0.1 + np.random.normal(0, 0.5, len(dates))

    df_response = pd.DataFrame({
        "날짜": dates,
        "소비자심리지수": consumer_sentiment,
        "마케팅 반응률(%)": response_rate
    })

    df_response["심리지수_저점"] = (
        (df_response["소비자심리지수"].shift(1) > df_response["소비자심리지수"]) &
        (df_response["소비자심리지수"].shift(-1) > df_response["소비자심리지수"])
    )
    df_response["추천 캠페인"] = np.where(df_response["심리지수_저점"], "\ud83d\udce2 회복기 타겟팅 캠페인 시작", "")

    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax1.set_title("소비자심리지수 vs 마케팅 반응률", fontsize=15)
    ax1.set_xlabel("월")
    ax1.set_ylabel("소비자심리지수", color="tab:blue")
    ax1.plot(df_response["날짜"], df_response["소비자심리지수"], color="tab:blue", marker='o')
    ax1.tick_params(axis='y', labelcolor="tab:blue")

    ax2 = ax1.twinx()
    ax2.set_ylabel("반응률 (%)", color="tab:green")
    ax2.plot(df_response["날짜"], df_response["마케팅 반응률(%)"], color="tab:green", marker='s', linestyle='--')
    ax2.tick_params(axis='y', labelcolor="tab:green")
    st.pyplot(fig)

    # 고객 인사이트 시각화
    st.markdown(" #### 고객 성향 분석")
    df_list = df_list.dropna(subset=['예상예산_만원'])
    df_list['예상예산_만원'] = df_list['예상예산_만원'].astype(float)
    fig = px.histogram(df_list, x="예상예산_만원", nbins=30, color_discrete_sequence=["#4B8BBE"])
    fig.update_layout(title="예상예산 분포", xaxis_title="예상예산 (만원)", yaxis_title="고객 수")
    st.plotly_chart(fig, use_container_width=True)

def create_realtime_chart():
    fig = go.Figure()
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=300
    )
    return fig

def economic_dashboard():
    st.title("실시간 경제지표 모니터링")
    
    # Kafka 컨슈머 설정
    consumer = KafkaConsumer(
        'exchange-rate',
        'interest-rate',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='latest'
    )
    
    # 실시간 데이터 버퍼
    rate_data = []
    interest_data = []
    
    placeholder = st.empty()
    
    for message in consumer:
        with placeholder.container():
            data = message.value
            
            # 실시간 데이터 업데이트
            if message.topic == 'exchange-rate':
                rate_data.append({'time': datetime.now(), 'value': data['value']})
            elif message.topic == 'interest-rate':
                interest_data.append({'time': datetime.now(), 'value': data['value']})
            
            # 대시보드 레이아웃
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🇺🇸 USD/KRW 환율")
                st.metric(
                    label="현재 환율", 
                    value=f"{rate_data[-1]['value']:.1f}원",
                    delta=f"{rate_data[-1]['value']-rate_data[-2]['value']:.1f}원" if len(rate_data)>1 else ""
                )
                fig = create_realtime_chart()
                fig.add_scatter(x=[d['time'] for d in rate_data[-30:]], 
                              y=[d['value'] for d in rate_data[-30:]],
                              name="환율 추이")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 🏦 기준금리")
                st.metric(
                    label="FED Rate", 
                    value=f"{interest_data[-1]['value']:.2f}%",
                    delta=f"{interest_data[-1]['value']-interest_data[-2]['value']:.2f}%" if len(interest_data)>1 else ""
                )
                fig = create_realtime_chart()
                fig.add_bar(x=[d['time'] for d in interest_data[-12:]], 
                          y=[d['value'] for d in interest_data[-12:]],
                          name="금리 변화")
                st.plotly_chart(fig, use_container_width=True)
    # 원본 데이터 보기
    st.subheader("🗂 원본 데이터 확인")
    with st.expander("GDP 실질 데이터"):
        st.dataframe(df_real.head())
    with st.expander("경제심리지수"):
        st.dataframe(df_sen.head())
    with st.expander("뉴스심리지수"):
        st.dataframe(df_news.head())
    with st.expander("고객 데이터"):
        st.dataframe(df_list.head())
    with st.expander("반응률/심리지수 통합 데이터"):
        st.dataframe(df_response)