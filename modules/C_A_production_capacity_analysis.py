# 생산·제조 현황 분석
# 현대자동차 생산 현황 실시간 모니터링 시스템
# 공장별 모델별 생산 현황 분석


import streamlit as st
import pandas as pd
import plotly.express as px

# 데이터 로드 함수
@st.cache_data
def load_data():
    df_inv = pd.read_csv("data/inventory_data.csv")
    df_list = pd.read_csv("data/hyundae_car_list.csv")
    return df_inv, df_list

# 생산 UI 함수
def capacity_analysis_ui():
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


        st.subheader("공장별 생산 가능 수량", divider="orange")

        # 생산가능수량 기준 집계
        model_summary = df_inv.groupby(['공장명','브랜드', '모델명', '트림명'])['생산가능수량']\
            .sum().reset_index().sort_values('생산가능수량', ascending=False)

        # 테이블 요약
        st.dataframe(
            model_summary.style.format({'생산가능수량': '{:,}대'}),
            use_container_width=True,
            height=500
        )

        # 시각화: 상위 20개만 bar chart
        top_n = model_summary.head(20)

        fig = px.bar(
            top_n,
            x='생산가능수량',
            y='모델명',
            color='브랜드',
            orientation='h',
            title="<b>Top 20 모델 생산 가능 수량</b>",
            height=700
        )
        fig.update_layout(
            xaxis_title="생산가능수량(대)",
            yaxis_title="모델명",
            font=dict(size=14),
            yaxis={'categoryorder':'total ascending'}
        )
        st.plotly_chart(fig, use_container_width=True)