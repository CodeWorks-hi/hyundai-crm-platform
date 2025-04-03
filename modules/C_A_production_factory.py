# 생산·제조 현황 분석
# 현대자동차 생산 현황 실시간 모니터링 시스템

import streamlit as st
import pandas as pd
import plotly.express as px
from modules.C_A_production_factory_report import report_ui, treemap_ui

# 데이터 로드 함수
@st.cache_data
def load_data():
    df_inv = pd.read_csv("data/inventory_data.csv")
    df_list = pd.read_csv("data/hyundae_car_list.csv")
    df_inv['트림명'] = df_inv['트림명'].astype(str).str.strip()
    df_list['트림명'] = df_list['트림명'].astype(str).str.strip()
    return df_inv, df_list

# 생산 UI 함수
def factory_ui():
    df_inv, df_list = load_data()

    tab1, tab2, tab3 = st.tabs([" 생산 능력 분석", "부품 재고 현황", " 공장별 상세 리포트"])

    with tab1:
        report_ui(df_inv)

    with tab2:
        col1, col2 = st.columns([3, 1])
        with col1:
            treemap_ui(df_inv)

        # 핵심 부품 정보
        critical_parts = df_inv[df_inv['부품명'].isin(['배터리', '모터', 'ABS 모듈'])]
        pivot_table = critical_parts.pivot_table(
            index='부품명',
            columns='공장명',
            values='재고량',
            aggfunc='sum'
        ).fillna(0).astype(int)

        st.subheader(" 핵심 부품 현황", divider='orange')
        st.dataframe(
            pivot_table.style.format("{:,}")
            .background_gradient(cmap='YlGnBu', axis=1),
            height=200,
            use_container_width=True
        )

        with st.expander(" 부품별 상세 데이터", expanded=True):
            st.dataframe(
                df_inv[['부품명', '공장명', '재고량']]
                .groupby(['부품명', '공장명'])
                .sum()
                .reset_index()
                .sort_values('재고량', ascending=False),
                height=600,
                use_container_width=True,
                hide_index=True
            )

        min_stocks = critical_parts.groupby('부품명')['재고량'].min()
        for part, qty in min_stocks.items():
            if qty < 100:
                st.error(f"⚠️ {part} 최소재고 위험: {qty:,}개 (권장 ≥100)")

    with tab3:
        selected_factory = st.selectbox('공장 선택', df_inv['공장명'].unique(), key='factory_select')
        factory_data = df_inv[df_inv['공장명'] == selected_factory]

        parts_summary = factory_data.groupby('부품명')['재고량']\
            .agg(['sum', 'median', 'max'])\
            .rename(columns={'sum': '총재고', 'median': '중간값', 'max': '최대재고'})\
            .astype(int)\
            .sort_values('총재고', ascending=False)

        col1, col2 = st.columns([2, 3])
        with col1:
            st.subheader(f" {selected_factory} 부품 현황", divider='green')
            st.dataframe(
                parts_summary.style.format("{:,}")
                .background_gradient(subset=['총재고'], cmap='Blues'),
                height=600,
                use_container_width=True
            )

        with col2:
            st.subheader(f" {selected_factory} 재고 분포", divider='green')
            fig = px.bar(
                parts_summary.reset_index(),
                x='부품명',
                y='총재고',
                color='부품명',
                title=f"<b>{selected_factory} 부품별 재고 현황</b>",
                height=600
            )
            fig.update_layout(
                xaxis_title=None,
                yaxis_title="재고량",
                showlegend=False,
                font=dict(size=14)
            )
            st.plotly_chart(fig, use_container_width=True)

        with st.expander(" 원본 데이터 확인", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("차량 마스터 데이터", divider='gray')
                st.dataframe(
                    df_list,
                    height=400,
                    use_container_width=True,
                    hide_index=True
                )
            with col2:
                st.subheader("부품 재고 데이터", divider='gray')
                st.dataframe(
                    df_inv,
                    height=400,
                    use_container_width=True,
                    hide_index=True
                )
