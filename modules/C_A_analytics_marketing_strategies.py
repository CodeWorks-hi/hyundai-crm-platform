import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
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

def strategies_ui():
    df_real, df_nom, df_sen, df_news, df_list, df_event = load_data()

    st.markdown(" ### 마케팅 전략 분석 및 캠페인 제안")

    # 캠페인 전략 Top 5
    st.markdown(" #### 캠페인 전략 Top 5")

    with st.expander("① 금리/환율 기반 실시간 트리거"):
        st.markdown("**조건**: 기준금리 < 3%, 환율 > 1300원")
        st.code("if (interest_rate < 3.0) & (exchange_rate > 1300):\n    activate_campaign('환율보호 프로모션')", language="python")
        st.success("2024년 4월 전환율 22% 상승")

    with st.expander("② 소비자 심리 하락기 맞춤 할인"):
        st.markdown("**조건**: CCI < 75, 뉴스심리지수 하락")
        st.code("if consumer_index < 75:\n    send_campaign(title='불확실성 대비 할인', targets=price_sensitive_users)", language="python")
        st.metric("2025년 1월 결과", "주문량 41% 증가", "+18%")

    with st.expander("③ EV 충전소 타겟 캠페인"):
        st.image("https://example.com/ev_charging_map.jpg", width=600)
        st.caption("전기차 충전소 기반 지역 마케팅")

    with st.expander("④ AI 기반 유지비 절감 캠페인"):
        st.markdown("유가 변동 시 하이브리드 추천")
        st.progress(65, text="하이브리드 추천률 55%")

    with st.expander("⑤ 경기 회복기 리타겟팅"):
        st.code("if gdp_growth > 1.0:\n    send_retargeting(segment='침체기 미구매자')", language="python")
        st.success("ROI 4.8배 달성")

    # 확장 전략
    st.markdown(" #### 추가 전략 제안")
    with st.expander("⑥ 제조업 회복 → B2B 캠페인"):
        st.write("제조업 실질 GDP 상승 시 법인 고객 대상 프로모션")
    with st.expander("⑦ 고용 회복기 신차 구독 유도"):
        st.write("실업률 개선 시 월구독 신차 서비스 제공")
    with st.expander("⑧ 부동산 회복기 대형차 캠페인"):
        st.write("부동산 가격 상승기 SUV 프로모션 강조")
    with st.expander("⑨ 뉴스심리 회복 시 신차 발표"):
        st.write("뉴스심리지수 90 이상 상승기 신차 런칭")
    with st.expander("⑩ 글로벌 성장률 상승기 수출형 모델 강조"):
        st.write("해외 GDP 상승기 수출전략 모델 중심 캠페인")

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

    # 이벤트/공지/점검 표시
    st.markdown("---")
    col1, _, col2, _, col3 = st.columns([2, 0.1, 2, 0.1, 2])
    with col1:
        st.markdown("### 📢 이벤트")
        render_paginated_list(df_event, "이벤트", "이벤트_page")
    with col2:
        st.markdown("### 📋 공지사항")
        render_paginated_list(df_event, "공지사항", "공지_page")
    with col3:
        st.markdown("### ⚙️ 점검안내")
        render_paginated_list(df_event, "점검 안내", "점검_page")
