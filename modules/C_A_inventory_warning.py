# 재고 자동 경고 
# 글로벌 재고 최적화, 공급망 관리
# 경고 시스템

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import requests

# 1. 데이터 로드
car_info_path = "data/hyundae_car_list.csv"
inv_path = "data/inventory_data.csv"

df_car = pd.read_csv(car_info_path)
df_inv = pd.read_csv(inv_path)

# 2. 회전율 계산
np.random.seed(42)
df_inv["월평균입고"] = np.random.randint(50, 500, size=len(df_inv))
df_inv["월평균출고"] = np.random.randint(30, 400, size=len(df_inv))
df_inv["재고회전율"] = (df_inv["월평균출고"] / df_inv["재고량"]).replace([np.inf, -np.inf], 0).fillna(0).round(2)

# 임계값 기준 경고 플래그
threshold = 0.3
df_inv["경고"] = np.where(df_inv["재고회전율"] <= threshold, "⚠️ 경고", "정상")

# 3. 슬랙 메시지 전송 함수
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

    response = requests.post(SLACK_WEBHOOK_URL, json={"text": text, "link_names": 1})
    if response.status_code != 200:
        st.error(f"슬랙 전송 실패: {response.status_code} - {response.text}")

# 4. Streamlit UI
def warning_ui():
    st.title("🚨 글로벌 재고 회전율 경고 시스템")

    with st.expander(" 전체 재고 테이블 보기"):
        st.dataframe(df_inv, use_container_width=True)
        st.download_button("CSV 다운로드", data=df_inv.to_csv(index=False), file_name="inventory_turnover.csv")


     # 기본값 초기화
    risk_df = pd.DataFrame()

    if "경고등급" in df_inv.columns and "부품명" in df_inv.columns:
        risk_df = df_inv[(df_inv["경고등급"] != "정상") & (df_inv["부품명"] != "미확인부품")]

    st.markdown("###### 🔥 긴급 조치 필요 항목")
    st.dataframe(
        risk_df[risk_df["경고등급"] == "🚨 긴급"],
        column_order=["공장코드", "부품명", "재고량", "재고회전율"],
        hide_index=True,
        height=300
    )

    st.markdown("###### 📌 주시 필요 항목")
    st.dataframe(
        risk_df[risk_df["경고등급"] == "⚠️ 주의"],
        column_order=["공장코드", "부품명", "재고량", "재고회전율"],
        hide_index=True,
        height=300
    )

    st.subheader("위험 부품 분포 분석", divider="red")
    fig2 = px.treemap(
        risk_df.dropna(subset=['공장코드', '부품명']),
        path=['공장코드', '부품명'],
        values='재고량',
        color='재고회전율',
        color_continuous_scale='Reds',
        height=600
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    warning_df = df_inv[df_inv["재고회전율"] <= threshold]

    with st.expander("📤 슬랙 경고 전송"):
        selected_models = st.multiselect("📌 슬랙으로 전송할 모델 선택", warning_df["모델명"].unique())
        filtered_df = warning_df[warning_df["모델명"].isin(selected_models)]

        if st.button("🚨 슬랙 전송"):
            for _, row in filtered_df.iterrows():
                send_slack_alert(
                    model_name=row["모델명"],
                    turnover_rate=row["재고회전율"],
                    plant=row["공장명"],
                    status=row["생산상태"],
                    link=f"https://example.com/cars/{row['모델명']}"
                )
            st.success("✅ 선택된 모델이 슬랙으로 전송되었습니다.")
