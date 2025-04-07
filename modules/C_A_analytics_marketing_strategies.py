import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import math
from datetime import datetime

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
    
    campaign_path = "data/campaign_list.csv"
    df_campaigns = pd.read_csv(campaign_path)
    today = datetime.today().date()
    df_campaigns["시작일"] = pd.to_datetime(df_campaigns["기간"].str.split("~").str[0].str.strip(), errors="coerce").dt.date
    df_campaigns["종료일"] = pd.to_datetime(df_campaigns["기간"].str.split("~").str[1].str.strip(), errors="coerce").dt.date
    df_campaigns["진행상태"] = df_campaigns.apply(
        lambda row: "진행 중" if row["시작일"] <= today <= row["종료일"]
        else "예정" if row["시작일"] > today
        else "종료", axis=1)


    # 전체 5개 컬럼 구성 (여백 0.15, 콘텐츠 컬럼 0.275씩)
    col1, col2, col3, col4, col5 = st.columns([0.05, 1, 0.05, 1, 0.05])

    # 캠페인 전략 Top 5
    with col2:
        st.header("이벤트 전략 Top 5")

        in_progress_events = df_campaigns[df_campaigns["진행상태"] == "진행 중"].head(5)
        for idx, row in in_progress_events.iterrows():
            with st.expander(f"{idx+1}. {row['이벤트명']}"):
                st.markdown(f"""
                - **대상**: {row['대상']}
                - **혜택**: {row['혜택']}
                - **참여 방법**: {row['참여 방법']}
                - **기간**: {row['기간']}
                - **전략 분류**: {row['분류']}
                """)

    # 추가 전략 제안
    with col4:
        st.header("추가 전략 제안")

        upcoming_events = df_campaigns[df_campaigns["진행상태"] == "예정"].head(5)
        for idx, row in upcoming_events.iterrows():
            with st.expander(f"{idx+1}. {row['이벤트명']}"):
                st.markdown(f"""
                - **대상**: {row['대상']}
                - **혜택**: {row['혜택']}
                - **참여 방법**: {row['참여 방법']}
                - **기간**: {row['기간']}
                - **전략 분류**: {row['분류']}
                """)

    st.markdown("---")

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
