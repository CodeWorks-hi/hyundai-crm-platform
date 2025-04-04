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
    st.markdown("### 실시간 공급망 리스크 모니터링 시스템")

    # 경고 임계값 설정 섹션
    with st.expander("⚙️ 분석 파라미터 설정", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            threshold = st.slider("⚠️ 회전율 경고 기준값", 0.1, 1.0, 0.3, 0.05,
                                help="재고 회전율 기준값 설정 (기본값: 0.3)")
        with col2:
            view_mode = st.selectbox("🔍 분석 모드 선택", 
                                ["공장-부품 계층 분석", "모델별 비교", "시간 추이 분석"])

    # 동적 경고 등급 계산
    df["경고등급"] = np.select(
        [df["재고회전율"] <= threshold*0.5, 
        df["재고회전율"] <= threshold],
        ["🚨 긴급", "⚠️ 주의"], 
        default="✅ 정상"
    )

    # 시각화 섹션
    st.subheader("🌐 글로벌 재고 상태 모니터링")

    if view_mode == "공장-부품 계층 분석":
        fig = px.treemap(
            df[df['공장명'] != 'UNK'],
            path=['공장명', '모델명', '부품명'],
            values='재고량',
            color='재고회전율',
            color_continuous_scale='RdYlGn_r',
            range_color=(0, 1),
            hover_data=['월평균입고', '월평균출고'],
            height=700,
            title=f"<b>계층적 재고 분석 (임계값: {threshold})</b>"
        )
        fig.update_traces(
            texttemplate="%{label}<br>%{value}개<br>회전율:%{color:.2f}",
            textposition="middle center"
        )

    elif view_mode == "모델별 비교":
        model_df = df.groupby('모델명', as_index=False).agg(
            총재고량=('재고량', 'sum'),
            평균회전율=('재고회전율', 'mean')
        )
        fig = px.bar(
            model_df.sort_values('평균회전율', ascending=False),
            x='모델명',
            y='평균회전율',
            color='총재고량',
            text_auto='.2f',
            height=700,
            labels={'평균회전율': '평균 재고 회전율'},
            title='<b>모델별 재고 효율 비교</b>',
            color_continuous_scale='Bluered_r'
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            uniformtext_minsize=8
        )

    elif view_mode == "시간 추이 분석":
        # 데이터 전처리
        trend_df = df.melt(
            id_vars=['공장명', '부품명'],
            value_vars=['월평균입고', '월평균출고'],
            var_name='구분',
            value_name='물동량'
        )
        
        # 공장별 물동량 집계
        factory_flow = trend_df.groupby(['공장명', '구분'])['물동량'].sum().reset_index()
        
        # 누적 바 차트
        fig = px.bar(
            factory_flow,
            x='공장명',
            y='물동량',
            color='구분',
            barmode='group',
            text='물동량',
            height=700,
            labels={'물동량': '월평균 물동량(개)'},
            color_discrete_sequence=['#4C78A8', '#F58518'],
            title='<b>공장별 월간 입출고 현황</b>'
        )
        
        # 레이아웃 개선
        fig.update_layout(
            xaxis=dict(
                title=None,
                tickangle=-45,
                type='category',
                categoryorder='total descending'
            ),
            yaxis=dict(
                title='물동량(개)',
                gridcolor='#F0F2F6'
            ),
            legend=dict(
                title='구분',
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            plot_bgcolor='white',
            uniformtext_minsize=8
        )
        
        # 데이터 레이블 포맷팅
        fig.update_traces(
            texttemplate='%{text:.0f}개',
            textposition='outside'
        )

    # 공통 레이아웃 설정
    fig.update_layout(
        margin=dict(t=50, l=25, r=25, b=25),
        coloraxis_colorbar=dict(
            title="회전율" if view_mode == "공장-부품 계층 분석" else "재고량",
            thickness=20
        ),
        plot_bgcolor='rgba(240,242,246,0.1)'
    )
    st.plotly_chart(fig, use_container_width=True)

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

