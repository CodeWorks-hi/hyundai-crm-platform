# 생산·제조 현황 분석
# 현대자동차 생산 현황 실시간 모니터링 시스템
# 부품 트리맵 생성 함수

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 데이터 로드 함수
@st.cache_data
def load_data():
    df_inv = pd.read_csv("data/inventory_data.csv")
    df_list = pd.read_csv("data/hyundae_car_list.csv")

    # 데이터 정제
    df_inv['트림명'] = df_inv['트림명'].astype(str).str.strip()
    df_list['트림명'] = df_list['트림명'].astype(str).str.strip()
    return df_inv, df_list

# 부품 트리맵 UI 함수
def treemap_ui(df_inv):
    st.subheader("공장-부품 계층적 재고 분포", divider='blue')

    part_inventory = df_inv.groupby(['공장명', '부품명'])['재고량'].sum().reset_index()

    fig = px.treemap(
        part_inventory,
        path=['공장명', '부품명'],
        values='재고량',
        color='재고량',
        color_continuous_scale='Blues',
        custom_data=['재고량'],
        height=800
    )

    fig.update_traces(
        texttemplate='<b>%{label}</b><br>%{value:,}개',
        hovertemplate='<b>%{label}</b><br>재고량: %{value:,}개<extra></extra>',
        textfont=dict(size=14),
        marker=dict(line=dict(width=1, color='DarkSlateGrey'))
    )

    fig.update_layout(
        title_text="부품 재고 트리맵",
        title_font_size=20,
        margin=dict(l=0, r=0, t=30, b=0),
        font=dict(size=14),
        height=800
    )

    st.plotly_chart(fig, use_container_width=True)

    # 핵심 부품 피벗 테이블
    critical_parts = df_inv[df_inv['부품명'].isin(['배터리', '모터', 'ABS 모듈'])]
    pivot_table = critical_parts.pivot_table(
        index='부품명',
        columns='공장명',
        values='재고량',
        aggfunc='sum'
    ).fillna(0).astype(int)

    st.subheader("핵심 부품 현황", divider='orange')
    st.dataframe(
        pivot_table.style.format("{:,}").background_gradient(cmap='YlGnBu', axis=1),
        height=200,
        use_container_width=True
    )

    min_stocks = critical_parts.groupby('부품명')['재고량'].min()
    for part, qty in min_stocks.items():
        if qty < 100:
            st.error(f"⚠️ {part} 최소재고 위험: {qty:,}개 (권장 ≥100)")