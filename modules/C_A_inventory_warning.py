# 재고 및 공급망 관리
    # 자동 재고 경고 시스템


# 📦 재고 회전율 분석 및 경고 시스템

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import requests

# ✅ 파일 경로 정의
car_info_path = "data/hyundae_car_list.csv"
inv_path = "data/inventory_data.csv"
ip_hyundai_path = "data/processed/생산 종료/fin-hyundai-by-car.csv"
fin_hyundai_path = "data/processed/생산 중/ip-hyundai-by-car.csv"
ip_kia_path = "data/processed/생산 종료/fin-kia-by-car.csv"
fin_kia_path = "data/processed/생산 중/ip-kia-by-car.csv"

# ✅ 데이터 불러오기
df_car = pd.read_csv(car_info_path)
df_inv = pd.read_csv(inv_path)
df_ip_hyundai = pd.read_csv(ip_hyundai_path)
df_fin_hyundai = pd.read_csv(fin_hyundai_path)
df_ip_kia = pd.read_csv(ip_kia_path)
df_fin_kia = pd.read_csv(fin_kia_path)

# ✅ 브랜드 병합
df_ip_hyundai["브랜드"] = "현대"
df_ip_kia["브랜드"] = "기아"
df_fin_hyundai["브랜드"] = "현대"
df_fin_kia["브랜드"] = "기아"
df_ip = pd.concat([df_ip_hyundai, df_ip_kia], ignore_index=True)
df_fin = pd.concat([df_fin_hyundai, df_fin_kia], ignore_index=True)

# ✅ 생산상태 병합
df_status = pd.merge(
    df_inv,
    df_fin[["차종"]].drop_duplicates().assign(생산상태="생산 중"),
    left_on="모델명", right_on="차종", how="left"
).drop(columns=["차종"])

df_status = pd.merge(
    df_status,
    df_ip[["차종"]].drop_duplicates().assign(생산상태="생산 종료"),
    left_on="모델명", right_on="차종", how="left"
)

df_status["생산상태"] = np.where(
    df_status["생산상태_y"].notna(), df_status["생산상태_y"],
    df_status["생산상태_x"].fillna("기타")
)
df_status.drop(columns=["차종", "생산상태_x", "생산상태_y"], inplace=True)

# ✅ 회전율 계산
turnover = df_status.groupby(["공장명", "브랜드", "모델명", "생산상태"]).agg({
    "재고량": "sum"
}).reset_index()

np.random.seed(42)
turnover["월평균입고"] = np.random.randint(50, 500, size=len(turnover))
turnover["월평균출고"] = np.random.randint(30, 400, size=len(turnover))
turnover["재고회전율"] = (turnover["월평균출고"] / turnover["재고량"]).replace([np.inf, -np.inf], 0).fillna(0).round(2)

# ✅ 경고 임계값 설정
threshold = 0.3
turnover["경고"] = np.where(turnover["재고회전율"] <= threshold, "⚠️ 경고", "정상")

# ✅ 슬랙 알림 함수 예시
slack_webhook_url = "https://hooks.slack.com/services/XXX/YYY/ZZZ"  # 실제 URL 입력

def send_slack_alert(model, rate):
    message = {
        "text": f"🚨 [경고] 모델 `{model}`의 재고회전율이 {rate}로 매우 낮습니다. 점검 요망."
    }
    requests.post(slack_webhook_url, json=message)

# ✅ Streamlit 앱

def warning_ui():
    st.title("🚨 자동 재고 경고 시스템")

    # 회전율 데이터 표시
    with st.expander(" 전체 회전율 데이터 보기", expanded=False):
        st.dataframe(turnover, use_container_width=True)

    # 경고 데이터 필터링
    warning_df = turnover[turnover["경고"] == "⚠️ 경고"].sort_values("재고회전율")

    st.subheader("⚠️ 회전율 경고 모델 (회전율 ≤ 0.3)")
    st.dataframe(warning_df, use_container_width=True)

    # Plotly 시각화
    with st.expander(" 공장별 재고 회전율 (Bubble Chart)"):
        fig = px.scatter(
            turnover,
            x="공장명", y="재고회전율",
            size="재고량",
            color="경고",
            hover_data=["모델명", "월평균출고", "생산상태"],
            title="공장별 모델 회전율 분석"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Seaborn 시각화
    with st.expander("📈 브랜드별 생산상태별 평균 회전율 (Bar Chart)"):
        plt.figure(figsize=(12, 6))
        sns_plot = sns.barplot(data=turnover, x="브랜드", y="재고회전율", hue="생산상태")
        plt.title("브랜드 및 생산상태별 평균 재고회전율")
        plt.ylabel("재고회전율")
        plt.xlabel("브랜드")
        plt.grid(True, axis="y")
        st.pyplot(plt.gcf())

    # 슬랙 알림 (버튼)
    if st.button("📤 슬랙 경고 전송 "):
        for _, row in warning_df.iterrows():
            send_slack_alert(row["모델명"], row["재고회전율"])
        st.success("경고 메시지가 슬랙으로 전송되었습니다 ✅")



    