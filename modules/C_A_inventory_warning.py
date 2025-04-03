import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import requests



# 📁 데이터 경로
car_info_path = "data/hyundae_car_list.csv"
inv_path = "data/inventory_data.csv"
ip_hyundai_path = "data/processed/생산 종료/fin-hyundai-by-car.csv"
fin_hyundai_path = "data/processed/생산 중/ip-hyundai-by-car.csv"
ip_kia_path = "data/processed/생산 종료/fin-kia-by-car.csv"
fin_kia_path = "data/processed/생산 중/ip-kia-by-car.csv"

# 📊 데이터 불러오기
df_car = pd.read_csv(car_info_path)
df_inv = pd.read_csv(inv_path)
df_ip_hyundai = pd.read_csv(ip_hyundai_path)
df_fin_hyundai = pd.read_csv(fin_hyundai_path)
df_ip_kia = pd.read_csv(ip_kia_path)
df_fin_kia = pd.read_csv(fin_kia_path)

# 🔗 브랜드 통합
df_ip_hyundai["브랜드"] = "현대"
df_ip_kia["브랜드"] = "기아"
df_fin_hyundai["브랜드"] = "현대"
df_fin_kia["브랜드"] = "기아"
df_ip = pd.concat([df_ip_hyundai, df_ip_kia], ignore_index=True)
df_fin = pd.concat([df_fin_hyundai, df_fin_kia], ignore_index=True)

# 🚗 생산상태 병합
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

# 🔢 회전율 계산
turnover = df_status.groupby(["공장명", "브랜드", "모델명", "생산상태"]).agg({
    "재고량": "sum"
}).reset_index()

np.random.seed(42)
turnover["월평균입고"] = np.random.randint(50, 500, size=len(turnover))
turnover["월평균출고"] = np.random.randint(30, 400, size=len(turnover))
turnover["재고회전율"] = (turnover["월평균출고"] / turnover["재고량"]).replace([np.inf, -np.inf], 0).fillna(0).round(2)

# 🚨 임계값 기준
threshold = 0.3
turnover["경고"] = np.where(turnover["재고회전율"] <= threshold, "⚠️ 경고", "정상")

# 🧾 슬랙 Webhook 연결
SLACK_WEBHOOK_URL = st.secrets["SLACK_WEBHOOK_URL"]

def send_slack_alert(model_name, turnover_rate, plant=None, status=None, link=None):
    emoji = "⚠️" if turnover_rate < 0.2 else "🔔"

    text = (
        f"{emoji} *재고 회전율 경고 발생!*\n"
        f"• 모델명: *{model_name}*\n"
        f"• 회전율: *{turnover_rate:.2f}*\n"
    )

    if plant:
        text += f"• 공장: `{plant}`\n"
    if status:
        text += f"• 생산상태: `{status}`\n"
    if link:
        text += f"🔗 <{link}|차량 상세정보 보기>\n"

    payload = {
        "text": text,
        "link_names": 1  # 멘션 지원용 (예: @here)
    }

    response = requests.post(SLACK_WEBHOOK_URL, json=payload)

    # 응답 확인
    if response.status_code == 200:
        st.success("✅ 슬랙 메시지가 정상적으로 전송되었습니다.")
    else:
        st.error(f"❌ 슬랙 전송 실패: {response.status_code} - {response.text}")

# 🖥️ Streamlit UI
def warning_ui():
    st.title("🚨 자동 재고 경고 시스템")

    with st.expander("📄 전체 회전율 테이블"):
        st.dataframe(turnover, use_container_width=True)
        st.download_button("CSV 다운로드", data=turnover.to_csv(index=False), file_name="turnover_warning.csv")

    with st.expander("📊 공장별 재고 회전율 (Bubble Chart)"):
        fig = px.scatter(
            turnover,
            x="공장명", y="재고회전율",
            size="재고량",
            color="경고",
            hover_data=["모델명", "월평균출고", "생산상태"]
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("📈 브랜드별 생산상태별 평균 회전율 (Bar Chart)"):
        plt.figure(figsize=(10, 5))
        sns.barplot(data=turnover, x="브랜드", y="재고회전율", hue="생산상태")
        plt.grid(True, axis="y")
        st.pyplot(plt.gcf())

    warning_df = turnover[turnover["재고회전율"] <= 0.3]

    with st.expander("📤 슬랙 경고 전송"):
        if st.button("🚨 슬랙으로 경고 전송"):
            if not warning_df.empty:
                for _, row in warning_df.iterrows():
                    send_slack_alert(
                        model_name=row["모델명"],
                        turnover_rate=row["재고회전율"],
                        plant=row.get("공장명", ""),
                        status=row.get("생산상태", ""),
                        link=f"https://example.com/cars/{row['모델명']}"
                    )
                st.success("✅ 슬랙으로 경고 메시지가 전송되었습니다.")
            else:
                st.info("⚠️ 현재 회전율 임계값 이하 모델이 없습니다.")

