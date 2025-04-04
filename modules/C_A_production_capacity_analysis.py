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

    df_merged = pd.merge(df_inv, df_list[['트림명', '모델명', '모델 구분']], on='트림명', how='left')
    summary = df_merged.groupby(['모델명', '모델 구분', '트림명'])['생산가능수량'].min().reset_index()

    os.makedirs("data/processed", exist_ok=True)
    summary.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    return summary, df_inv

# 생산 가능 수량 및 재고 동시 감소 함수
def process_order(model_name, trim_name):
    df_inv = pd.read_csv(INV_PATH)
    df_summary = pd.read_csv(OUTPUT_PATH)

    idx = df_summary[(df_summary['모델명'] == model_name) & (df_summary['트림명'] == trim_name)].index
    if not idx.empty:
        df_summary.loc[idx[0], '생산가능수량'] = max(0, df_summary.loc[idx[0], '생산가능수량'] - 1)

    mask = (df_inv['모델명'] == model_name) & (df_inv['트림명'] == trim_name)
    df_inv.loc[mask, '재고량'] = df_inv.loc[mask, '재고량'] - 1
    df_inv['재고량'] = df_inv['재고량'].clip(lower=0)

    df_summary.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    df_inv.to_csv(INV_PATH, index=False, encoding="utf-8-sig")
    return df_summary, df_inv

# Streamlit UI 시작
st.markdown(" ### 모델별 생산 가능 수량 자동 생성 및 발주 처리")

# STEP 1 - 생성
if st.button("🔄 model_trim_capacity.csv 생성"):
    df_summary, df_inv = generate_capacity_file()
    st.success("✅ 파일 생성 완료!")
    st.subheader(" 생성된 생산가능 수량 미리보기")
    st.dataframe(df_summary, use_container_width=True)

# STEP 2 - 딜러 발주
st.markdown("---")
st.markdown(" ####  딜러 발주 시뮬레이션")

if os.path.exists(OUTPUT_PATH):
    df_summary = pd.read_csv(OUTPUT_PATH)
    model_list = df_summary['모델명'].unique().tolist()

    col1, col2 = st.columns(2)
    with col1:
        selected_model = st.selectbox("모델명", model_list)
    with col2:
        trim_list = df_summary[df_summary['모델명'] == selected_model]['트림명'].unique().tolist()
        selected_trim = st.selectbox("트림명", trim_list)

    if st.button(" 딜러 발주 처리 (-1)"):
        df_summary, df_inv = process_order(selected_model, selected_trim)
        st.success(f"🎉 {selected_model} / {selected_trim} 발주 처리 완료!")

        st.subheader(" 업데이트된 생산 가능 수량")
        st.dataframe(df_summary, use_container_width=True)

        st.subheader("🔧 관련 부품 재고 변경 확인")
        affected = df_inv[(df_inv['모델명'] == selected_model) & (df_inv['트림명'] == selected_trim)]
        st.dataframe(affected[['공장명', '부품명', '재고량']], use_container_width=True)
else:
    st.warning("먼저 [🔄 model_trim_capacity.csv 생성] 버튼을 눌러주세요.")

# 시각화 섹션
st.markdown("---")
st.header("📊 전체 생산 가능 수량 분석")

if os.path.exists(OUTPUT_PATH):
    model_summary = pd.read_csv(OUTPUT_PATH)

    tab1, tab2 = st.tabs(["📋 상세 데이터", "📈 시각화 분석"])

    with tab1:
        with st.expander("📦 전체 생산 가능 수량 요약", expanded=True):
            st.dataframe(
                model_summary.style.format({'생산가능수량': '{:,}대'}),
                use_container_width=True,
                height=500,
                column_config={
                    "생산가능수량": st.column_config.ProgressColumn(
                        "가능 수량",
                        help="최소 재고량 기반 생산 가능 대수",
                        format="%d대",
                        min_value=0,
                        max_value=model_summary['생산가능수량'].max()
                    )
                }
            )

    with tab2:
        fig = px.bar(
            model_summary.head(20),
            x='생산가능수량',
            y='모델명',
            color='모델 구분',
            orientation='h',
            title="<b>TOP 20 모델 생산 계획</b>",
            height=700,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(
            xaxis_title="생산 가능 수량(대)",
            yaxis_title="모델명",
            font=dict(size=14),
            yaxis={'categoryorder':'total ascending'},
            hoverlabel=dict(bgcolor="white", font_size=12)
        )
        st.plotly_chart(fig, use_container_width=True)

    if model_summary['생산가능수량'].min() < 100:
        st.error(
            f"경고: {model_summary.loc[model_summary['생산가능수량'].idxmin(), '모델명']} 모델 재고 위험",
            icon="🚨"
        )
