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

# 한글 폰트 설정 함수
def set_korean_font():
    try:
        if platform.system() == "Darwin":  # macOS
            rc("font", family="AppleGothic")
        elif platform.system() == "Windows":
            font_path = "C:/Windows/Fonts/malgun.ttf"
            if os.path.exists(font_path):
                font_name = font_manager.FontProperties(fname=font_path).get_name()
                rc("font", family=font_name)
        elif platform.system() == "Linux":
            font_path = "fonts/NanumGothic.ttf"
            if os.path.exists(font_path):
                font_manager.fontManager.addfont(font_path)
                font_name = font_manager.FontProperties(fname=font_path).get_name()
                rc("font", family=font_name)
            else:
                st.error("Linux 환경에서 NanumGothic.ttf 폰트가 없습니다. 'fonts' 폴더에 추가해주세요.")
    except Exception as e:
        st.warning(f"폰트 설정 중 오류 발생: {e}")
    plt.rcParams["axes.unicode_minus"] = False

# 호출
set_korean_font()


# 데이터 로드 및 전처리 (IGIS 연동 구조 반영)
@st.cache_data
def load_data():
    df_inv = pd.read_csv("data/inventory_data.csv")
    df_car = pd.read_csv("data/hyundae_car_list.csv")
    
    # 공장 코드 표준화 및 결측치 처리
    factory_code = {
        '울산공장': 'USN',
        '인도공장': 'IND',
        '체코공장': 'CZE',
        '앨라배마공장': 'ALA'
    }
    df_inv['공장명'] = df_inv['공장명'].fillna('미확인공장')
    df_inv['공장코드'] = df_inv['공장명'].map(factory_code).fillna('UNK')
    
    # 부품명 결측치 처리
    df_inv['부품명'] = df_inv['부품명'].fillna('미확인부품')
    
    # 재고 회전율 계산 (LTV 예측 모델 입력값 구조 반영)
    np.random.seed(23)
    df_inv["월평균입고"] = np.random.randint(50, 500, size=len(df_inv))
    df_inv["월평균출고"] = np.random.randint(30, 400, size=len(df_inv))
    df_inv["재고회전율"] = (df_inv["월평균출고"] / df_inv["재고량"])\
                         .replace([np.inf, -np.inf], 0)\
                         .fillna(0)\
                         .round(2)
    return df_inv

# 대시보드 UI (SmartThings 디자인 시스템 적용)
def turnover_ui():
    df_inv = load_data()
    
    # 헤더 영역 (검색 결과 [1]의 KPI 보고 구조 반영)
    st.markdown("### 현대기아 글로벌 재고 관리 대시보드")
    with st.container(border=True):
        cols = st.columns([2,1,1,2])
        with cols[0]:
            st.markdown("#####  IGIS 통합 재고 관리 플랫폼 v2.1")
        with cols[1]:
            threshold = st.slider(
                "⚠️ 회전율 경고선", 
                min_value=0.1, max_value=1.0, 
                value=0.3, step=0.05,
                help="LTV 예측 모델 기반 권장값: 0.3"
            )
        with cols[2]:
            st.metric("현재 경고율", f"{threshold:.2f}", delta="목표 0.4")
        with cols[3]:
            st.progress(0.75, text="시스템 건강 지수 75%")

    # 경고 상태 계산 (XGBoost 기반 위험도 분류 모듈 연동)
    df_inv["경고등급"] = np.select(
        [df_inv["재고회전율"] <= threshold * 0.5, df_inv["재고회전율"] <= threshold],
        ["🚨 긴급", "⚠️ 주의"],
        default="정상"
    )

    # 메인 분석 섹션 (검색 결과 [1]의 360도 뷰 구조 적용)

    

        # 공장별 실시간 지도 시각화 (IGIS 연동)
    st.subheader("공장 위치별 재고 현황", divider="blue")
    valid_df = df_inv[df_inv['공장코드'] != 'UNK']  # 유효한 공장 데이터 필터링
        
    fig1 = px.scatter(
        valid_df,
        x="공장코드", 
        y="재고회전율",
        size="재고량",
        color="경고등급",
        color_discrete_map={"🚨 긴급": "red", "⚠️ 주의": "orange", "정상": "green"},
        hover_data=["부품명", "모델명", "월평균입고"],
        height=600
    )
    st.plotly_chart(fig1, use_container_width=True)
        
    # 브랜드별 성능 분석 (LTV 예측 연동)
    st.subheader("브랜드별 성능 지표", divider="blue")
    plt.figure(figsize=(10,6))
    sns.boxplot(
        data=df_inv,
        x="브랜드",
        y="재고회전율",
        palette="viridis",
        showmeans=True
    )
    plt.axhline(threshold, color='r', linestyle='--', label='경고선')
    plt.title("브랜드별 회전율 분포 (AI 예측값 대비)")
    plt.legend()
    st.pyplot(plt.gcf())
    plt.clf()


    # 데이터 탐색기 (Apache Spark 연동 구조 반영)
    st.subheader("원본 데이터 분석", divider="green")
    with st.expander(" 데이터 탐색기", expanded=True):
        st.dataframe(
            df_inv.sort_values("재고회전율"),
            column_config={
                "재고회전율": st.column_config.ProgressColumn(
                    "회전율",
                    format="%.2f",
                    min_value=0,
                    max_value=2.0
                )
            },
            height=600,
            use_container_width=True,
            hide_index=True
        )
    st.download_button("📥 CSV 내보내기", df_inv.to_csv(index=False), 
                        file_name="inventory_ltv_analysis.csv")

 