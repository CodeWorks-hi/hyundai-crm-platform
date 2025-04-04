# 생산·제조 현황 분석
# 현대자동차 생산 현황 실시간 모니터링 시스템

import streamlit as st
import pandas as pd
import plotly.express as px
from .C_A_production_factory_report import report_ui
from .C_A_production_factory_treemap import treemap_ui

# 데이터 로드 함수
@st.cache_data
def load_data():
    df_inv = pd.read_csv("data/inventory_data.csv")
    df_list = pd.read_csv("data/hyundae_car_list.csv")
    return df_inv, df_list

# 생산 UI 함수
def factory_ui():
    df_inv, df_list = load_data()

    # 생산 분석 리포트 생성
    with st.spinner("생산 분석 데이터 처리 중..."):
        prod_capacity = df_inv.groupby(['공장명', '모델명', '트림명'])['재고량'].min()
        total_prod = prod_capacity.groupby('공장명').sum().reset_index(name='생산가능수량')

        inventory_analysis = df_inv.groupby('공장명').agg(
            총재고량=('재고량', 'sum'),
            평균재고=('재고량', 'mean'),
            고유부품수=('부품명', 'nunique')
        ).reset_index()

        report = pd.merge(total_prod, inventory_analysis, on='공장명')
        report['생산효율'] = (report['생산가능수량'] / report['총재고량'] * 100).round(2)

        report = report.astype({
            '생산가능수량': 'int',
            '총재고량': 'int',
            '고유부품수': 'int'
        })
        st.subheader("현대자동차 생산 현황 실시간 모니터링 시스템")

        cols = st.columns(4)
        st.markdown("""<style>.stMetric {padding: 20px; background-color: #f8f9fa; border-radius: 10px;}</style>""", unsafe_allow_html=True)

        cols[0].metric("총 부품 재고", f"{int(report['총재고량'].sum()):,}개", help="전체 공장의 부품 재고 총합")
        cols[1].metric("최대 생산 가능", f"{int(report['생산가능수량'].max()):,}대", report.loc[report['생산가능수량'].idxmax(), '공장명'])
        cols[2].metric("최고 생산 효율", f"{float(report['생산효율'].max()):.2f}%", report.loc[report['생산효율'].idxmax(), '공장명'])
        cols[3].metric("평균 회전율", f"{float(report['생산효율'].mean()):.1f}%", help="전체 공장의 평균 재고 회전율")

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["공장별 상세 리포트", "생산 능력 분석", "부품 재고 현황"])

    #  TAB 1 - 공장별 상세 리포트
    with tab1:


        st.markdown("---")

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
                st.dataframe(df_list, height=400, use_container_width=True, hide_index=True)
            with col2:
                st.subheader("부품 재고 데이터", divider='gray')
                st.dataframe(df_inv, height=400, use_container_width=True, hide_index=True)


    # TAB 2 - 생산 능력 분석 (트리맵)
    with tab2:
        treemap_ui(df_inv)


    # TAB 3 - 부품 재고 현황 (종합 분석)
    with tab3:
        report_ui(df_inv)
