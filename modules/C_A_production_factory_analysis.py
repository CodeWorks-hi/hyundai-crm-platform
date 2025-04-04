# 생산·제조 현황 분석
# 현대자동차 생산 현황 실시간 모니터링 시스템
# 공장별 모델별 생산 현황 분석


import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 경로 설정
INV_PATH = "data/inventory_data.csv"
LIST_PATH = "data/hyundae_car_list.csv"
OUTPUT_PATH = "data/model_trim_capacity.csv"

# 데이터 로드 함수
def load_data():
    df_inv = pd.read_csv(INV_PATH)
    df_list = pd.read_csv(LIST_PATH)
    return df_inv, df_list

# CSV 생성 함수
def generate_capacity_file():
    df_inv = pd.read_csv(INV_PATH)
    df_list = pd.read_csv(LIST_PATH)

    df_inv['트림명'] = df_inv['트림명'].astype(str).str.strip()
    df_list['트림명'] = df_list['트림명'].astype(str).str.strip()

    df_merged = pd.merge(df_inv,df_list[['트림명', '모델명', '모델 구분']],on='트림명',how='left')
    summary = df_merged.groupby(['모델명', '모델 구분', '트림명'])['생산가능수량'].min().reset_index()

    os.makedirs("data/processed", exist_ok=True)
    summary.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    return summary, df_inv

# 생산 가능 수량 및 재고 동시 감소 함수 (공장 지정 포함)
def process_order(model_name, trim_name, factory_name):
    df_inv = pd.read_csv(INV_PATH)
    df_summary = pd.read_csv(OUTPUT_PATH)

    idx = df_summary[(df_summary['모델명'] == model_name) & (df_summary['트림명'] == trim_name)].index
    if not idx.empty:
        df_summary.loc[idx[0], '생산가능수량'] = max(0, df_summary.loc[idx[0], '생산가능수량'] - 1)

    mask = (
        (df_inv['모델명'] == model_name) &
        (df_inv['트림명'] == trim_name) &
        (df_inv['공장명'] == factory_name)
    )
    df_inv.loc[mask, '재고량'] = df_inv.loc[mask, '재고량'] - 1
    df_inv.loc[mask, '생산가능수량'] = df_inv.loc[mask, '생산가능수량'] - 1

    df_inv['재고량'] = df_inv['재고량'].clip(lower=0)
    df_inv['생산가능수량'] = df_inv['생산가능수량'].clip(lower=0)

    df_summary.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    df_inv.to_csv(INV_PATH, index=False, encoding="utf-8-sig")
    return df_summary, df_inv

# Streamlit UI 시작
def factory_analysis_ui():
    st.markdown(" ### 생산 제조 현황 실시간 모니터링")

    if not os.path.exists(OUTPUT_PATH):
        st.warning("먼저 [🔄 model_trim_capacity.csv 생성]이 필요합니다.")
        return

    df_summary = pd.read_csv(OUTPUT_PATH)
    df_inv = pd.read_csv(INV_PATH)

    # 전체 생산 현황 요약
    st.markdown(" #### 모델별 생산 가능 수량")
    st.dataframe(df_summary, use_container_width=True)

    # 모델별 집계
    model_summary = df_summary.groupby(['모델명', '모델 구분'])['생산가능수량'].sum().reset_index()

    st.markdown("---")
    st.markdown(" #### 생산 가능 모델 TOP 20 ")

    fig = px.bar(
        model_summary.sort_values("생산가능수량", ascending=False).head(20),
        x='생산가능수량',
        y='모델명',
        color='모델 구분',
        orientation='h',
        title="<b>TOP 20 생산 계획 현황</b>",
        height=700,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(
        xaxis_title="생산 가능 수량(대)",
        yaxis_title="모델명",
        font=dict(size=14),
        yaxis={'categoryorder': 'total ascending'},
        hoverlabel=dict(bgcolor="white", font_size=12)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader(" 공장별 부품 재고 요약")

    factory_parts = df_inv.groupby(['공장명', '부품명'], as_index=False)['재고량'].sum()
    st.dataframe(factory_parts, use_container_width=True)

    st.markdown("---")
    st.subheader(" 재고 위험 알림")

    danger_parts = df_inv[df_inv['재고량'] < 100][['공장명', '부품명', '재고량']]
    if not danger_parts.empty:
        st.error("📉 일부 부품 재고가 임계치 이하입니다.")
        st.dataframe(danger_parts, use_container_width=True)
    else:
        st.success("✅ 모든 부품 재고가 정상입니다.")
