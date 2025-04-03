# 재고 자동 경고 
    # 글로벌 재고 최적화, 공급망 관리
        # 재고 회전율 경고 시스템
            # 재고 회전율이 임계값 이하인 경우 슬랙으로 경고 메시지 전송

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import requests

# 파일 경로
car_info_path = "data/hyundae_car_list.csv"
inv_path = "data/inventory_data.csv"
ip_hyundai_path = "data/processed/생산 종료/fin-hyundai-by-car.csv"
fin_hyundai_path = "data/processed/생산 중/ip-hyundai-by-car.csv"
ip_kia_path = "data/processed/생산 종료/fin-kia-by-car.csv"
fin_kia_path = "data/processed/생산 중/ip-kia-by-car.csv"

# 데이터 로드
df_car = pd.read_csv(car_info_path)
df_inv = pd.read_csv(inv_path)
df_ip_hyundai = pd.read_csv(ip_hyundai_path)
df_fin_hyundai = pd.read_csv(fin_hyundai_path)
df_ip_kia = pd.read_csv(ip_kia_path)
df_fin_kia = pd.read_csv(fin_kia_path)

# 브랜드 통합
df_ip_hyundai["브랜드"] = "현대"
df_ip_kia["브랜드"] = "기아"
df_fin_hyundai["브랜드"] = "현대"
df_fin_kia["브랜드"] = "기아"
df_ip = pd.concat([df_ip_hyundai, df_ip_kia], ignore_index=True)
df_fin = pd.concat([df_fin_hyundai, df_fin_kia], ignore_index=True)

# 생산상태 밀점
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

# 회전율 계산
turnover = df_status.groupby(["공장명", "브랜드", "모델명", "생산상태"]).agg({
    "재고량": "sum"
}).reset_index()

np.random.seed(42)
turnover["월평균입고"] = np.random.randint(50, 500, size=len(turnover))
turnover["월평균출고"] = np.random.randint(30, 400, size=len(turnover))
turnover["재고회전율"] = (turnover["월평균출고"] / turnover["재고량"]).replace([np.inf, -np.inf], 0).fillna(0).round(2)

# 임계값 기준
threshold = 0.3
df_warning = turnover.copy()
df_warning["경고"] = np.where(df_warning["재고회전율"] <= threshold, "⚠️ 경고", "정상")

# Slack webhook
SLACK_WEBHOOK_URL = st.secrets["SLACK_WEBHOOK_URL"]

def send_slack_summary(df):
    table_rows = "\n".join(
        [f"- *{row['모델명']}* | 회전율: `{row['재고회전율']}` | 공장: {row['공장명']} | 상태: {row['생산상태']}"
         for _, row in df.iterrows()]
    )
    message = {
        "text": "🚨 재고 회전율 경고 목록",
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": "🚨 *재고 회전율 경고 요약표*\n회전율이 0.3 이하인 모델 목록입니다."}},
            {"type": "section", "text": {"type": "mrkdwn", "text": table_rows}}
        ]
    }
    response = requests.post(SLACK_WEBHOOK_URL, json=message)
    if response.status_code != 200:
        raise ValueError(f"Slack 전송 실패: {response.status_code}, {response.text}")

def warning_ui():
    st.title("🚨 자동 재고 경고 시스템")

    with st.expander(" 전체 회전율 테이블"):
        st.dataframe(df_warning, use_container_width=True)
        st.download_button("CSV 다운로드", data=df_warning.to_csv(index=False), file_name="turnover_warning.csv")

    with st.expander(" 공장별 재고 회전율 (Bubble Chart)"):
        fig = px.scatter(
            df_warning,
            x="공장명", y="재고회전율",
            size="재고량",
            color="경고",
            hover_data=["모델명", "월평균출고", "생산상태"]
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander(" 브랜드별 생산상태별 평균 회전율 (Bar Chart)"):
        plt.figure(figsize=(10, 5))
        sns.barplot(data=df_warning, x="브랜드", y="재고회전율", hue="생산상태")
        plt.grid(True, axis="y")
        st.pyplot(plt.gcf())

    selected_models = st.multiselect("슬랙 전송할 모델을 선택하세요", df_warning[df_warning["경고"] == "⚠️ 경고"]["모델명"].unique())
    filtered_df = df_warning[df_warning["모델명"].isin(selected_models)]

    if st.button("📤 선택 모델 슬랙 전송"):
        if not filtered_df.empty:
            send_slack_summary(filtered_df)
            st.success("✅ 선택한 모델에 대한 경고가 슬랙으로 전송되었습니다.")
        else:
            st.info("선택된 모델이 없습니다.")
