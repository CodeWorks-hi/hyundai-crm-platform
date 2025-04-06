import streamlit as st
import pandas as pd
import joblib
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
import os
from io import BytesIO
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import plotly.express as px


@st.cache_data
def load_data():
    df_customer = pd.read_csv("data/customer_data.csv")
    df_export = pd.read_csv("data/export_customer_data.csv")
    df_domestic = pd.read_csv("data/domestic_customer_data.csv")
    df_list = pd.read_csv("data/customers.csv")  # 파일명 수정됨
    return df_customer, df_export, df_domestic, df_list


def preprocess_and_train_model(df):
    df = df.drop(columns=["이름", "연락처", "브랜드", "모델명", "공장명"], errors="ignore")

    df["고객 등급"] = np.random.choice(["VIP", "일반", "신규"], size=len(df))
    df["차량 유형"] = np.random.choice(["세단", "SUV", "해치백"], size=len(df))
    df["할부 여부"] = np.random.choice([0, 1], size=len(df))
    df["구매 경로"] = np.random.choice([0, 1], size=len(df))
    df["최근 거래 금액"] = np.random.randint(10000000, 40000000, size=len(df))
    df["누적 구매 금액"] = df["최근 거래 금액"] + np.random.randint(10000000, 30000000, size=len(df))
    df["평균 구매 금액"] = (df["최근 거래 금액"] + df["누적 구매 금액"]) // 2
    df["고객 충성도 지수"] = np.round(np.random.uniform(0.5, 1.0, size=len(df)), 2)
    df["고객 평생 가치"] = df["누적 구매 금액"] * df["고객 충성도 지수"]

    features = [
        "성별", "연령대", "거주 지역", "고객 등급", "차량 유형",
        "차량 구매 횟수", "할부 여부", "구매 경로",
        "최근 거래 금액", "누적 구매 금액", "평균 구매 금액", "고객 충성도 지수"
    ]
    target = "고객 평생 가치"
    categorical_cols = ["성별", "연령대", "거주 지역", "고객 등급", "차량 유형"]

    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    encoded = encoder.fit_transform(df[categorical_cols])
    encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out(categorical_cols))

    X = pd.concat([df.drop(columns=categorical_cols + [target]), encoded_df], axis=1)
    y = df[target]

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    model = XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)

    os.makedirs("model", exist_ok=True)
    joblib.dump(model, "model/xgb_domestic_ltv_model.pkl")

    return model, df, X


def generate_pdf_report(df_top10):
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont("Helvetica", 14)
    c.drawString(100, 800, "LTV 예측 리포트 상위 고객 10명")

    y = 760
    for i, row in df_top10.iterrows():
        line = f"{row['연령대']} / {row['거주 지역']} / 예측 LTV: {row['예측 LTV']:,.0f}원"
        c.drawString(80, y, line)
        y -= 20
        if y < 100:
            break

    c.save()
    buffer.seek(0)
    return buffer


def ltv_customer_ui():
    st.title(" LTV 고객 가치 예측 분석")

    df_customer, df_export, df_domestic, df_list = load_data()

    with st.spinner("모델 학습 및 예측 중..."):
        model, df_with_pred, X = preprocess_and_train_model(df_domestic)
        df_with_pred["예측 LTV"] = model.predict(X)

    st.success("✅ 모델 학습 및 예측 완료")

    # 예측 결과 시각화
    st.markdown("### 🔝 예측 LTV 기준 상위 고객 TOP 10")
    top10 = df_with_pred[["연령대", "거주 지역", "고객 평생 가치", "예측 LTV"]].sort_values("예측 LTV", ascending=False).head(10)
    st.dataframe(top10.style.format({'예측 LTV': '{:,.0f}원'}), height=400)

    st.markdown("---")
    
    st.markdown("###  예측 결과 시각화")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔹 예측 vs 실제 LTV 오차 분포")
        df_with_pred["LTV 오차"] = df_with_pred["고객 평생 가치"] - df_with_pred["예측 LTV"]
        fig1, ax1 = plt.subplots()
        ax1.hist(df_with_pred["LTV 오차"], bins=20, color='salmon', edgecolor='black')
        ax1.set_title("예측 오차 분포 (실제 - 예측)")
        ax1.set_xlabel("LTV 오차 (원)")
        ax1.set_ylabel("고객 수")
        st.pyplot(fig1)

        st.markdown("""
        #### 🔸 1. 예측 오차 분포 분석
        - 위의 **히스토그램은 고객 별 실제 LTV와 예측 LTV 간의 차이**를 보여줍니다.
        - 분포 중심이 0에 가까울수록 모델이 전반적으로 정확하게 예측하고 있다는 것을 의미합니다.
        - 만약 오차가 한쪽으로 치우쳐 있다면, 특정 그룹(예: 고소득 고객)에 대해 과소/과대 평가가 이루어지고 있을 가능성이 있습니다.
        """)

    with col2:
        st.markdown("#### 🔹 예측 vs 실제 LTV 비교 (상위 20명)")
        top20 = df_with_pred.sort_values("고객 평생 가치", ascending=False).head(20).reset_index()
        fig2, ax2 = plt.subplots()
        ax2.plot(top20.index, top20["고객 평생 가치"], label="실제 LTV", marker='o')
        ax2.plot(top20.index, top20["예측 LTV"], label="예측 LTV", marker='x')
        ax2.set_title("상위 20명 고객 LTV 비교")
        ax2.set_xlabel("고객 순위")
        ax2.set_ylabel("LTV (원)")
        ax2.legend()
        st.pyplot(fig2)
        st.markdown("""
                #### 🔸 2. 상위 고객 20명 비교 분석
                - 실선은 **실제 LTV**, 점선은 **모델이 예측한 LTV**를 나타냅니다.
                - 고객 순위가 높을수록(= 더 가치 있는 고객일수록), 예측값과 실제값 간 차이가 커질 가능성이 있습니다.
                - 특히 상위 5~10명에서 예측값이 일관되게 낮거나 높은 경우, 해당 구간에 대한 **모델 개선의 여지**가 존재합니다.
                    """)

    st.markdown("---")

    # 리포트 다운로드
    st.markdown("###  리포트 다운로드")
    pdf_buffer = generate_pdf_report(top10)
    st.download_button(
        label="📥 LTV 예측 리포트 다운로드",
        data=pdf_buffer,
        file_name="ltv_report.pdf",
        mime="application/pdf"
    )


    st.markdown("### 고객 맞춤 추천")

    if "연령대" in df_with_pred.columns and "거주 지역" in df_with_pred.columns:
        selected_age = st.selectbox("연령대 선택", df_with_pred["연령대"].unique())
        selected_region = st.selectbox("거주 지역 선택", df_with_pred["거주 지역"].unique())

        recommended = df_with_pred[
            (df_with_pred["연령대"] == selected_age) &
            (df_with_pred["거주 지역"] == selected_region)
        ].sort_values("예측 LTV", ascending=False).head(5)

        st.markdown(f"**추천 고객 TOP 5 (연령대: {selected_age}, 지역: {selected_region})**")
        st.dataframe(recommended[["연령대", "거주 지역", "예측 LTV"]])
    else:
        st.warning("연령대 또는 거주 지역 정보가 부족합니다.")


    # 📌 원본 데이터 확인
    st.markdown("###  원본 데이터 확인")
    with st.expander(" 원본 데이터 확인"):
        tab1, tab2, tab3 = st.tabs(["딜러 상담 리스트", "국내 판매 고객데이터", "해외 판매 고객데이터"])

        with tab1:
            st.dataframe(df_list, use_container_width=True, hide_index=True)

        with tab2:
            # 임의 재고 데이터 생성 또는 df_customer 사용
            df_inv = df_customer.copy()
            st.dataframe(df_inv, use_container_width=True, hide_index=True)

        with tab3:
            # 임의 공장 데이터 생성 또는 df_export 사용
            df_plant = df_export.copy()
            st.dataframe(df_plant, use_container_width=True, hide_index=True)