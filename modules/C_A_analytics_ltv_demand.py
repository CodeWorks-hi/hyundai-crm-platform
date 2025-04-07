# 판매·\uuc218\uuc218\uc출 관리
#     LTV 모델 결과, 시장 특징, 예측 배후 및 발주 관리

import streamlit as st
import pandas as pd
from prophet import Prophet
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
import numpy as np

@st.cache_data
def load_data():
    df_customer = pd.read_csv("data/customer_data.csv")
    df_export = pd.read_csv("data/export_customer_data.csv")
    df_inventory = pd.read_csv("data/inventory_data.csv")
    return df_customer, df_export, df_inventory


# 모델 파일 경로
DOMESTIC_MODEL_PATH = "model/xgb_domestic_ltv_model.pkl"
EXPORT_MODEL_PATH = "model/xgb_export_ltv_model.pkl"

# 모델 로드
try:
    domestic_model = joblib.load(DOMESTIC_MODEL_PATH)
    export_model = joblib.load(EXPORT_MODEL_PATH)
except Exception as e:
    st.error(f"LTV 모델 로드 오류: {e}")

    # 재현성 보장을 위한 시드 설정
    np.random.seed(42)

def ltv_demand_ui():
    df_customer, df_export, df_inventory = load_data()

    df_combined = pd.concat([
        df_customer[["최근 구매 제품", "최근 구매 날짜"]],
        df_export[["\ucd5c\uadfc \uad6c\ub9e4 \uc81c\ud488", "\ucd5c\uadfc \uad6c\ub9e4 \ub0a0\uc9dc"]],
    ])

    df_combined["최근 구매 날짜"] = pd.to_datetime(df_combined["최근 구매 날짜"], errors="coerce")
    df_combined = df_combined.dropna(subset=["최근 구매 제품", "최근 구매 날짜"])

    model_options = df_combined["최근 구매 제품"].value_counts().index.tolist()
    selected_model = st.selectbox("차량 모델을 선택하세요", model_options)

    df_model = df_combined[df_combined["최근 구매 제품"] == selected_model]
    df_model = df_model.groupby("최근 구매 날짜").size().reset_index(name="y")
    df_model = df_model.rename(columns={"최근 구매 날짜": "ds"}).sort_values("ds")

    if len(df_model) < 10:
        st.warning("데이터가 부족하여 예측이 어렵습니다.")
        return

    model = Prophet()
    model.fit(df_model)
    future = model.make_future_dataframe(periods=90)
    forecast = model.predict(future)
    total_demand = forecast.tail(90)["yhat"].sum()

    df_parts = df_inventory[df_inventory["모델명"] == selected_model].copy()
    df_parts["예상 소요량"] = (total_demand / len(df_parts)).round()
    df_parts["남은 재고"] = df_parts["재고량"] - df_parts["예상 소요량"]

    st.markdown(f"###  {selected_model}  수요 예측(향후 90일)")
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(x=df_model["ds"], y=df_model["y"], name="실제 판매량",
               marker_color='#1f77b4', opacity=0.7),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=forecast["ds"], y=forecast["yhat"], name="예측 수요량",
                   line=dict(color='#ff7f0e', width=3, dash='dot'),
                   mode='lines+markers'),
        secondary_y=True
    )

    fig.add_trace(
        go.Scatter(
            x=forecast["ds"].tolist() + forecast["ds"].tolist()[::-1],
            y=forecast["yhat_upper"].tolist() + forecast["yhat_lower"].tolist()[::-1],
            fill='toself', fillcolor='rgba(255,127,14,0.2)',
            line=dict(color='rgba(255,255,255,0)'), name="신뢰구간", hoverinfo="skip"
        ),
        secondary_y=True
    )

    fig.update_layout(
        title='<b>월별 판매 현황 및 수요 예측</b>',
        xaxis=dict(title='날짜', tickformat='%Y-%m'),
        yaxis=dict(title='실제 판매량 (개)'),
        yaxis2=dict(title='예측 수요량 (개)', overlaying='y', side='right'),
        hovermode="x unified",
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("###  공장별 부품 소요량 예측")
    st.dataframe(df_parts[["공장명", "부품명", "재고량", "예상 소요량", "남은 재고"]], use_container_width=True, hide_index=True)
    st.info(f" 전체 예측 수요량 (90일): **{int(total_demand):,} 대**")

    st.markdown("###  자동 발주 제안")
    min_threshold = st.number_input(" 재고 최소 임계값 (예: 200)", min_value=0, value=200)

    df_parts["남은 재고"] = df_parts["재고량"] - df_parts["예상 소요량"]
    df_parts["발주 필요 여부"] = df_parts["남은 재고"] < min_threshold
    df_parts["발주 수량"] = ((df_parts["예상 소요량"] + min_threshold) - df_parts["재고량"]).clip(lower=0).round()

    df_order = df_parts[df_parts["발주 필요 여부"]]

    if df_order.empty:
        st.success("✅ 모든 부품의 재고가 충분합니다.")
    else:
        st.warning(f"🚨 총 {len(df_order)}건의 부품에 대해 발주가 필요합니다.")
        st.dataframe(
            df_order[["공장명", "부품명", "재고량", "예상 소요량", "남은 재고", "발주 수량"]],
            use_container_width=True, hide_index=True
        )
        csv = df_order.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 발주 목록 다운로드 (CSV)",
            data=csv,
            file_name=f"{selected_model}_order_list.csv",
            mime="text/csv"
        )
