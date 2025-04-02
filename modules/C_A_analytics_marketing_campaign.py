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


def marketing_campaign_ui():
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

    dates = pd.date_range(start="2023-01-01", periods=12, freq="M")
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
