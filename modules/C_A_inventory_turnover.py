# 재고 및 공급망 관리
    # 재고 회전율 분석
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import platform
from matplotlib import font_manager, rc
import os

# 🔤 한글 폰트 설정
def set_korean_font():
    try:
        if platform.system() == "Darwin":
            rc("font", family="AppleGothic")
        elif platform.system() == "Windows":
            font_path = "C:/Windows/Fonts/malgun.ttf"
            font_name = font_manager.FontProperties(fname=font_path).get_name()
            rc("font", family=font_name)
        elif platform.system() == "Linux":
            font_path = "fonts/NanumGothic.ttf"
            if os.path.exists(font_path):
                font_manager.fontManager.addfont(font_path)
                font_name = font_manager.FontProperties(fname=font_path).get_name()
                rc("font", family=font_name)
        plt.rcParams["axes.unicode_minus"] = False
    except Exception as e:
        st.warning(f"폰트 설정 오류: {e}")

set_korean_font()

# 📦 데이터 로드
@st.cache_data
def load_data():
    df_inv = pd.read_csv("data/inventory_data.csv")
    factory_code = {'울산공장': 'USN', '인도공장': 'IND', '체코공장': 'CZE', '앨라배마공장': 'ALA'}
    df_inv['공장코드'] = df_inv['공장명'].map(factory_code).fillna('UNK')
    df_inv['부품명'] = df_inv['부품명'].fillna('미확인부품')

    np.random.seed(23)
    df_inv["월평균입고"] = np.random.randint(50, 500, size=len(df_inv))
    df_inv["월평균출고"] = np.random.randint(30, 400, size=len(df_inv))
    df_inv["재고회전율"] = (df_inv["월평균출고"] / df_inv["재고량"])\
        .replace([np.inf, -np.inf], 0).fillna(0).round(2)
    return df_inv

# 🎯 메인 UI
def turnover_ui():
    df = load_data()
    
    st.title("📦 글로벌 재고 회전율 분석 대시보드")
    st.markdown("AI 기반 LTV 예측 및 공급망 위험 조기 경고 시스템")

    threshold = st.slider("⚠️ 회전율 경고 기준값", 0.1, 1.0, 0.3, 0.05)
    
    df["경고등급"] = np.select(
        [df["재고회전율"] <= threshold * 0.5, df["재고회전율"] <= threshold],
        ["🚨 긴급", "⚠️ 주의"], default="✅ 정상"
    )

    # 📍 공장별 회전율 산점도
    st.subheader("🏭 공장별 재고 회전율")
    fig1 = px.scatter(
        df[df['공장코드'] != 'UNK'],
        x="공장코드", y="재고회전율",
        size="재고량",
        color="경고등급",
        hover_data=["부품명", "모델명", "월평균입고"],
        color_discrete_map={"🚨 긴급": "red", "⚠️ 주의": "orange", "✅ 정상": "green"},
        height=600
    )
    st.plotly_chart(fig1, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
    # 📊 브랜드별 회전율 분포
        st.subheader(" 브랜드별 회전율 박스플롯")
        plt.figure(figsize=(10,6))
        sns.boxplot(data=df, x="브랜드", y="재고회전율", palette="pastel")
        plt.axhline(threshold, color='red', linestyle='--', label='경고 기준선')
        plt.title("브랜드별 회전율 분포")
        plt.legend()
        st.pyplot(plt.gcf())
        plt.clf()
    with col2:
    # ⏱️ 트림별 회전율 히스토그램
        st.subheader("트림별 회전율 히스토그램")
        plt.figure(figsize=(10,6))
        sns.histplot(df["재고회전율"], bins=30, kde=True, color='skyblue')
        plt.axvline(threshold, color='red', linestyle='--', label='경고 기준선')
        plt.title("전체 부품 회전율 분포")
        plt.xlabel("재고 회전율")
        plt.ylabel("빈도")
        plt.legend()
        st.pyplot(plt.gcf())
        plt.clf()

    # 🔥 Top/Bottom 10 부품
    st.subheader(" 회전율 상위/하위 부품 TOP 10")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🔝 상위 10개 부품**")
        st.dataframe(df.sort_values("재고회전율", ascending=False).head(10)[["공장명", "부품명", "재고회전율", "재고량"]])

    with col2:
        st.markdown("**🔻 하위 10개 부품**")
        st.dataframe(df.sort_values("재고회전율", ascending=True).head(10)[["공장명", "부품명", "재고회전율", "재고량"]])

    # [6] 원본 데이터 보기
    with st.expander(" 원본 데이터 보기", expanded=False):
        st.dataframe(df, use_container_width=True, hide_index=True)

    # CSV 다운로드
    st.download_button("📥 분석 결과 다운로드", df.to_csv(index=False), file_name="inventory_turnover_analysis.csv")

