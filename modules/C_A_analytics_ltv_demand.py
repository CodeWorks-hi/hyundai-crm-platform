# 판매·수출 관리
#     LTV 모델 결과, 시장 트렌드, 예측 분석
#         수요 예측 및 발주 관리


import streamlit as st
import pandas as pd
from prophet import Prophet
import plotly.graph_objects as go

@st.cache_data
def load_data():
    df_customer = pd.read_csv("data/customer_data.csv")
    df_export = pd.read_csv("data/export_customer_data.csv")
    df_inventory = pd.read_csv("data/inventory_data.csv")
    return df_customer, df_export, df_inventory

def ltv_demand_ui():
    # 데이터 불러오기
    df_customer, df_export, df_inventory = load_data()

    # 최근 구매 제품 기준 통합
    df_combined = pd.concat([
        df_customer[["최근 구매 제품", "최근 구매 날짜"]],
        df_export[["최근 구매 제품", "최근 구매 날짜"]],
    ])

    # 날짜 처리
    df_combined["최근 구매 날짜"] = pd.to_datetime(df_combined["최근 구매 날짜"], errors="coerce")
    df_combined = df_combined.dropna(subset=["최근 구매 제품", "최근 구매 날짜"])

    # 차량 모델 선택
    model_options = df_combined["최근 구매 제품"].value_counts().index.tolist()
    selected_model = st.selectbox("차량 모델을 선택하세요", model_options)

    # 선택 모델 기준 수요 집계
    df_model = df_combined[df_combined["최근 구매 제품"] == selected_model]
    df_model = df_model.groupby("최근 구매 날짜").size().reset_index(name="y")
    df_model = df_model.rename(columns={"최근 구매 날짜": "ds"}).sort_values("ds")

    # 데이터 부족 경고
    if len(df_model) < 10:
        st.warning("데이터가 부족하여 예측이 어렵습니다.")
        return

    # Prophet 예측
    model = Prophet()
    model.fit(df_model)
    future = model.make_future_dataframe(periods=90)
    forecast = model.predict(future)
    total_demand = forecast.tail(90)["yhat"].sum()

    # 공장별 부품 소요량 계산
    df_parts = df_inventory[df_inventory["모델명"] == selected_model].copy()
    df_parts["예상 소요량"] = (total_demand / len(df_parts)).round()
    df_parts["남은 재고"] = df_parts["재고량"] - df_parts["예상 소요량"]

    # 시각화
    st.markdown(f"###  {selected_model}  수요 예측(향후 90일)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat"], name="예측 수요량"))
    fig.add_trace(go.Bar(x=df_model["ds"], y=df_model["y"], name="실제 판매량"))
    st.plotly_chart(fig, use_container_width=True)

    # 소요량 테이블
    st.markdown("###  공장별 부품 소요량 예측")
    st.dataframe(df_parts[["공장명", "부품명", "재고량", "예상 소요량", "남은 재고"]], use_container_width=True)
    st.info(f" 전체 예측 수요량 (90일): **{int(total_demand):,} 대**")

    # 발주 기준 설정
    st.markdown("###  자동 발주 제안")
    min_threshold = st.number_input(" 재고 최소 임계값", min_value=0, value=200)

    df_parts["발주 필요 여부"] = df_parts["남은 재고"] < min_threshold
    df_parts["발주 수량"] = (df_parts["예상 소요량"] - df_parts["재고량"]).clip(lower=0).round()

    # 발주 대상 필터링
    df_order = df_parts[df_parts["발주 필요 여부"] == True]

    if df_order.empty:
        st.success("✅ 모든 부품의 재고가 충분합니다.")
    else:
        st.warning(f"🚨 총 {len(df_order)}건의 부품에 대해 발주가 필요합니다.")
        st.dataframe(df_order[["공장명", "부품명", "재고량", "예상 소요량", "남은 재고", "발주 수량"]], use_container_width=True)

        csv = df_order.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 발주 목록 다운로드 (CSV)",
            data=csv,
            file_name=f"{selected_model}_order_list.csv",
            mime="text/csv"
        )
