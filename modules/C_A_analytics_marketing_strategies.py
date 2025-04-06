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

    st.title("📊 마케팅 전략 분석 및 예측 기반 캠페인 제안")

    # 캠페인 전략 Top 5
    st.markdown("### ✅ 캠페인 전략 Top 5")
    with st.expander("① 금리/환율 기반 실시간 트리거"):
        st.code("if (interest_rate < 3.0) & (exchange_rate > 1300):\n    activate_campaign('환율보호 프로모션')", language="python")
        st.success("2024년 4월 전환율 22% 상승")

    with st.expander("② 소비자 심리 하락기 맞춤 할인"):
        st.code("if consumer_index < 75:\n    send_campaign(title='불확실성 대비 할인')", language="python")
        st.metric("2025년 1월 결과", "주문량 41% 증가", "+18%")

    with st.expander("③ EV 충전소 타겟 캠페인"):
        st.image("https://example.com/ev_charging_map.jpg", width=600)
        st.caption("전기차 충전소 기반 지역 마케팅")

    with st.expander("④ AI 기반 유지비 절감 캠페인"):
        st.progress(65, text="하이브리드 추천률 55%")

    with st.expander("⑤ 경기 회복기 리타겟팅"):
        st.code("if gdp_growth > 1.0:\n    send_retargeting(segment='침체기 미구매자')", language="python")

    # 확장 전략
    st.markdown("### 🌍 추가 전략 제안")
    st.markdown("- 제조업 회복 → B2B 캠페인\n- 고용 회복기 신차 구독 유도\n- 부동산 회복기 SUV 캠페인\n- 뉴스심리 회복 시 신차 발표\n- 글로벌 GDP 성장 시 수출 모델 강조")

    # GDP 실질 성장률 시각화
    st.subheader("📈 국내총생산(GDP) 실질 추이")
    df_gdp = df_real[df_real["계정항목"] == "국내총생산(시장가격, GDP)"].copy().set_index("계정항목").T
    df_gdp.columns = ["GDP"]
    df_gdp = df_gdp.applymap(lambda x: float(str(x).replace(",", "")))
    df_gdp["분기"] = df_gdp.index
    fig_gdp = px.line(df_gdp, x="분기", y="GDP", title="국내총생산(GDP) 실질 추이", markers=True)
    st.plotly_chart(fig_gdp, use_container_width=True)

    # 소비자심리지수 vs 반응률
    st.subheader("📉 소비자심리지수 vs 마케팅 반응률")
    dates = pd.date_range("2022-01-01", periods=24, freq="M")
    consumer_sentiment = np.random.normal(90, 5, size=24)
    response_rate = 5 + (consumer_sentiment - np.mean(consumer_sentiment)) * 0.1 + np.random.normal(0, 0.5, 24)
    df_response = pd.DataFrame({"날짜": dates, "소비자심리지수": consumer_sentiment, "마케팅 반응률(%)": response_rate})
    df_response["심리지수_저점"] = (df_response["소비자심리지수"].shift(1) > df_response["소비자심리지수"]) & \
                                   (df_response["소비자심리지수"].shift(-1) > df_response["소비자심리지수"])
    df_response["추천 캠페인"] = np.where(df_response["심리지수_저점"], "📢 회복기 타겟팅", "")
    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(df_response["날짜"], df_response["소비자심리지수"], color="tab:blue", marker="o")
    ax2 = ax1.twinx()
    ax2.plot(df_response["날짜"], df_response["마케팅 반응률(%)"], color="tab:green", marker="s", linestyle="--")
    st.pyplot(fig)

    # 고객 예산 분석
    st.subheader("💰 고객 예상 예산 분포")
    df_list = df_list.dropna(subset=['예상예산_만원'])
    df_list['예상예산_만원'] = df_list['예상예산_만원'].astype(float)
    fig = px.histogram(df_list, x="예상예산_만원", nbins=30, title="예상예산 분포", color_discrete_sequence=["#4B8BBE"])
    st.plotly_chart(fig, use_container_width=True)

    # 뉴스심리지수 NLP 요약
    st.subheader("📰 뉴스심리지수 요약 (AI 기반)")
    avg_news = df_news["뉴스심리지수"].tail(12).mean()
    st.info(f"최근 1년 평균 뉴스심리지수: **{avg_news:.2f}** → {'긍정적' if avg_news > 100 else '부정적'} 분위기")

    # 고객 세그먼트별 캠페인 성과
    st.subheader("👥 세그먼트별 캠페인 성과 비교")
    if "세그먼트" in df_list.columns and "캠페인응답률" in df_list.columns:
        seg_df = df_list.groupby("세그먼트")["캠페인응답률"].mean().reset_index()
        fig = px.bar(seg_df, x="세그먼트", y="캠페인응답률", color="세그먼트", title="세그먼트별 응답률")
        st.plotly_chart(fig, use_container_width=True)

    # 이벤트 공지사항
    st.subheader("📢 이벤트 및 공지사항")
    col1, _, col2, _, col3 = st.columns([2, 0.1, 2, 0.1, 2])
    with col1:
        st.markdown("### 🎉 이벤트")
        render_paginated_list(df_event, "이벤트", "이벤트_page")
    with col2:
        st.markdown("### 📋 공지사항")
        render_paginated_list(df_event, "공지사항", "공지_page")
    with col3:
        st.markdown("### ⚙️ 점검안내")
        render_paginated_list(df_event, "점검 안내", "점검_page")
