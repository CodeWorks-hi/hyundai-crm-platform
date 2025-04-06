import streamlit as st
import pandas as pd
import joblib
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
import os



@st.cache_data
def load_data():
    df_customer = pd.read_csv("data/customer_data.csv")
    df_export = pd.read_csv("data/export_customer_data.csv")
    df_domestic = pd.read_csv("data/domestic_customer_data.csv")
    df_list = pd.read_csv("data/customer.csv")
    return df_customer, df_export, df_domestic, df_list

# 모델 학습 및 전처리 함수
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

    joblib.dump(model, "model/xgb_domestic_ltv_model.pkl")

    return model, df, X

# Streamlit 메인 실행 함수
def ltv_customer_ui():
    st.title("📈 LTV 고객 가치 예측 분석")

    df_customer, df_export, df_domestic, df_list = load_data()

    with st.spinner("모델 학습 및 예측 중..."):
        model, df_with_pred, X = preprocess_and_train_model(df_domestic)
        df_with_pred["예측 LTV"] = model.predict(X)

    st.success("✅ 모델 학습 및 예측 완료")

    st.markdown("### 🔝 예측 LTV 기준 상위 고객 TOP 10")
    top10 = df_with_pred[["연령대", "거주 지역", "고객 평생 가치", "예측 LTV"]].sort_values("예측 LTV", ascending=False).head(10)
    st.dataframe(top10.style.format({'예측 LTV': '{:,.0f}원'}), height=400)

    st.markdown("---")
    st.markdown("### 📂 전체 데이터 미리보기")
    st.dataframe(df_with_pred.head(20))

    st.markdown("### 📄 리포트 다운로드")
    st.download_button(
        label="📥 LTV 예측 리포트 다운로드",
        data=pdf_buffer,
        file_name="ltv_report.pdf",
        mime="application/pdf"
    )

    st.markdown("### 🧠 고객 맞춤 추천")

    selected_age = st.selectbox("연령대 선택", df["연령대"].unique())
    selected_region = st.selectbox("거주 지역 선택", df["거주 지역"].unique())

    recommended = df[
        (df["연령대"] == selected_age) &
        (df["거주 지역"] == selected_region)
    ].sort_values("예측 LTV", ascending=False).head(5)

    st.markdown(f"**추천 고객 TOP 5 (연령대: {selected_age}, 지역: {selected_region})**")
    st.dataframe(recommended[["이름", "연령대", "거주 지역", "예측 LTV"]])    