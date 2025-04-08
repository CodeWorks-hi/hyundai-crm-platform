import streamlit as st
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from kafka import KafkaConsumer
import json
import plotly.graph_objects as go
from datetime import datetime

TEXT_MODEL_ID = "google/gemma-2-9b-it"
API_TOKEN = st.secrets.get("HUGGINGFACE_API_TOKEN")

if not API_TOKEN:
    st.error("❌ Hugging Face API 토큰이 설정되지 않았습니다.")
    st.stop()

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
    df_campaigns = pd.read_csv("data/campaign_list.csv")  # CSV 경로 확인
    selected_campaign = st.selectbox("분석할 이벤트을 선택하세요", df_campaigns["이벤트명"].unique())

    if st.button("선택한 이벤트 AI 인사이트 생성"):
        selected = df_campaigns[df_campaigns["이벤트명"] == selected_campaign].iloc[0]

        with st.spinner("KoAlpaca가 인사이트를 분석 중입니다..."):
            import requests
            HF_API_URL = f"https://api-inference.huggingface.co/models/{TEXT_MODEL_ID}"
            headers = {"Authorization": f"Bearer {API_TOKEN}"}

            prompt = f"""
다음 마케팅 이벤트을 다음 항목별로 요약 분석해줘:

1. 전략 분석
2. 기대 효과
3. 시장 전망

이벤트명: {selected['이벤트명']}
대상: {selected['대상']}
혜택: {selected['혜택']}
참여 방법: {selected['참여 방법']}
기간: {selected['기간']}
전략 분류: {selected['분류']}

결과를 항목별로 나누어 정리해줘.
"""

            res = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt})
            if res.status_code == 200:
                result = res.json()
                if isinstance(result, list) and "generated_text" in result[0]:
                    st.markdown(f"#### 📌 {selected_campaign} 분석 결과")
                    st.success(result[0]["generated_text"])
                else:
                    st.warning("AI 응답 형식을 이해할 수 없습니다.")
            else:
                st.error("AI 분석 요청에 실패했습니다. API Key나 모델 상태를 확인해주세요.")

    st.header("기대 효과 및 분석")

    st.markdown("""
    - **전시장 유입 증가**: 시승 및 유류비 제공 전략으로 신규 리드 유입 예상  
    - **SUV 집중 판매 상승**: 캠핑 테마 혜택으로 레저 수요층 공략 → SUV 중심 판매 증대  
    - **브랜드 이미지 제고**: 콘서트, 캠핑, 여행 연계로 감성 마케팅 강화 → MZ세대 공감 유도  
    - **충성 고객 관리 체계화**: 장기 고객 대상 교체 보상 프로그램으로 재구매율 향상 기대  
    - **디지털 기반 확장 가능성**: Streamlit 기반 페이지 구성으로 모바일/온라인 전환 대응 용이
    """)

    # 이벤트별 응답률 예시 데이터
    campaign_data = pd.DataFrame({
        "이벤트명": ["전기차 시승권 제공", "보상판매 리타겟팅", "무이자 금융 프로모션", "SUV 비교체험단"],
        "응답률(%)": [12.5, 8.3, 10.2, 7.1],
        "전환율(%)": [5.4, 3.9, 4.6, 3.2],
        "ROI": [2.8, 1.9, 2.3, 1.7]
    })

    # 응답률 & 전환율 바차트
    st.subheader(" 이벤트별 응답률 & 전환율")
    fig = px.bar(campaign_data, x="이벤트명", y=["응답률(%)", "전환율(%)"],
                 barmode="group", color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)



    #  ROI 추이
    st.subheader(" ROI 추이")
    fig2 = px.line(campaign_data, x="이벤트명", y="ROI", markers=True)
    st.plotly_chart(fig2, use_container_width=True)

    # 👉 추천 액션
    st.markdown("####  추천 액션")
    st.markdown("""
    - `응답률 10% 이상 이벤트` 중심으로 **예산 재배분**
    - `ROI 2.0 이상` 이벤트은 **전국 확대 검토**
    - `전기차·SUV 세그먼트` → 시승 기반 프로모션 지속 필요
    """)

    st.markdown("""

    - **전시장 유입 촉진**: 전기차 시승 기회 및 유류비 지원을 통한 신규 고객 유입 가능성 증가
    - **SUV 세그먼트 타겟팅**: 캠핑·레저 테마 중심 혜택 구성 → MZ세대 중심 SUV 전환율 상승 기대
    - **브랜드 감성 이미지 강화**: 콘서트, 여행, 캠핑 등 감성적 체험 제공으로 브랜드 충성도 제고
    - **ROI 기반 캠페인 선별 운영**: ROI 2.0 이상 캠페인에 대한 전국 확산 검토 권장
    - **전기차 우선 캠페인 유지**: 응답률 10% 이상인 '전기차 시승 캠페인'을 중심으로 예산 집중 필요
    """)
    st.markdown("---")


    # 📉 뉴스심리지수 vs 응답률 (시계열 비교)
    st.subheader(" 뉴스심리지수 vs 이벤트응답률 추이")

    dates = pd.date_range(start="2023-01-01", periods=12, freq="MS")
    news_sentiment = pd.Series([95, 90, 88, 92, 97, 85, 82, 78, 80, 87, 91, 94], index=dates, name="뉴스심리지수")
    response_rate = pd.Series([4.2, 4.0, 3.8, 4.1, 4.6, 3.5, 3.3, 3.1, 3.2, 3.8, 4.0, 4.3], index=dates, name="응답률 (%)")

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.set_title("뉴스심리지수 vs 마케팅 이벤트응답률", fontsize=16)
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
    st.markdown("""
        - **뉴스심리지수 하락기**(6~8월): 응답률도 동반 하락 → 사회적 분위기가 소비심리와 연동됨
        - **심리지수 회복기**(10~12월): 응답률 점진적 회복 → 연말 이벤트의 긍정적 반응 확인
        - **마케팅 타이밍 전략 필요**: 심리지수 하락 전 선제적 프로모션이 효과적
        """)
    
def create_realtime_chart():
    fig = go.Figure()
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=300
    )
    return fig

def economic_dashboard():

    st.title("실시간 경제지표 모니터링")
    st.markdown("---")
    
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

            # AI 인사이트 분석 버튼
            if st.button(f"AI 인사이트 보기: {row['이벤트명']}", key=f"ai_insight_inprogress_{idx}"):
                with st.spinner("AI가 이벤트을 분석 중입니다..."):
                    import requests
                    HF_API_URL = f"https://api-inference.huggingface.co/models/{TEXT_MODEL_ID}"
                    headers = {"Authorization": f"Bearer {API_TOKEN}"}
                    prompt = f"다음 마케팅 이벤트의 전략을 분석해주고, 기대 효과와 시장 전망을 요약해줘.\n\n이벤트명: {row['이벤트명']}\n대상: {row['대상']}\n혜택: {row['혜택']}\n참여 방법: {row['참여 방법']}\n기간: {row['기간']}\n전략 분류: {row['분류']}\n\n결과:"
                    res = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt})
                    if res.status_code == 200:
                        result = res.json()
                        if isinstance(result, list) and "generated_text" in result[0]:
                            st.markdown("**📌 AI 분석 결과**")
                            st.success(result[0]["generated_text"])
                        else:
                            st.warning("AI 응답 형식을 이해할 수 없습니다.")
                    else:
                        st.error("AI 분석 요청에 실패했습니다. API Key나 모델 상태를 확인해주세요.")

            # 기존 정의 오류 방지용, 실제 정의는 다른 곳에서 처리됨
            upcoming_events = [] if 'upcoming_events' not in locals() else upcoming_events
            
            # upcoming_events 반복문 내에도 AI 인사이트 분석 버튼 추가
            for idx, row in upcoming_events.iterrows():
                with st.expander(f"{idx+1}. {row['이벤트명']}"):
                    st.markdown(f"""
                    - **대상**: {row['대상']}
                    - **혜택**: {row['혜택']}
                    - **참여 방법**: {row['참여 방법']}
                    - **기간**: {row['기간']}
                    - **전략 분류**: {row['분류']}
                    """)

                    # AI 인사이트 분석 버튼
                    if st.button(f"AI 인사이트 보기: {row['이벤트명']}", key=f"ai_insight_upcoming_{idx}"):
                        with st.spinner("AI가 이벤트을 분석 중입니다..."):
                            import requests
                            HF_API_URL = f"https://api-inference.huggingface.co/models/{TEXT_MODEL_ID}"
                            headers = {"Authorization": f"Bearer {API_TOKEN}"}
                            prompt = f"다음 마케팅 이벤트의 전략을 분석해주고, 기대 효과와 시장 전망을 요약해줘.\n\n이벤트명: {row['이벤트명']}\n대상: {row['대상']}\n혜택: {row['혜택']}\n참여 방법: {row['참여 방법']}\n기간: {row['기간']}\n전략 분류: {row['분류']}\n\n결과:"
                            res = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt})
                            if res.status_code == 200:
                                result = res.json()
                                if isinstance(result, list) and "generated_text" in result[0]:
                                    st.markdown("**📌 AI 분석 결과**")
                                    st.success(result[0]["generated_text"])
                                else:
                                    st.warning("AI 응답 형식을 이해할 수 없습니다.")
                            else:
                                st.error("AI 분석 요청에 실패했습니다. API Key나 모델 상태를 확인해주세요.")
