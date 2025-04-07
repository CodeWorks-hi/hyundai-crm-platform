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


# 모델 파일 경로
DOMESTIC_MODEL_PATH = "model/xgb_domestic_ltv_model.pkl"
EXPORT_MODEL_PATH = "model/xgb_export_ltv_model.pkl"

# 모델 로드
try:
    domestic_model = joblib.load(DOMESTIC_MODEL_PATH)
    export_model = joblib.load(EXPORT_MODEL_PATH)
except Exception as e:
    st.error(f"LTV 모델 로드 오류: {e}")


np.random.seed(42) 

@st.cache_data
def load_data():
    df_customer = pd.read_csv("data/customer_data.csv")
    df_export = pd.read_csv("data/export_customer_data.csv")
    df_domestic = pd.read_csv("data/domestic_customer_data.csv")
    df_list = pd.read_csv("data/customers.csv") 
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



    # 예측 결과 시각화
    st.markdown("### 🔝 예측 LTV 기준 상위 고객 TOP 10")
    top10 = df_with_pred[["연령대", "거주 지역", "고객 평생 가치", "예측 LTV"]].sort_values("예측 LTV", ascending=False).head(10)
    st.dataframe(top10.style.format({'예측 LTV': '{:,.0f}원'}), height=400)

    st.markdown("---")

    # 예측 결과 시각화
    st.markdown("### 예측 결과 시각화")

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
        - 분포 중심이 0에 가까워진다면 모델이 전반적으로 예측을 잘하고 있다는 것을 의미합니다.
        - 오차가 하나의 방향으로 치우쳐 있다면, 특정 그룹에 대해 과소/과대 평가가 이루어졌을 가능성이 있습니다.
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
        - 고객 순위가 높을수록(= 더 가치 있는 고객일수록), 예측값과 실제값 간 차이가 커질 수 있습니다.
        - 특히 상위 5~10명에서 예측값이 일관되게 낮거나 높다면, 해당 구간에 대한 **모델 개선의 여지**가 존재합니다.
        """)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🎯 예측값에 따른 잔차 산점도 (잔차)")
        df_with_pred["잔차"] = df_with_pred["고객 평생 가치"] - df_with_pred["예측 LTV"]
        fig_residual, ax_residual = plt.subplots()
        ax_residual.scatter(df_with_pred["예측 LTV"], df_with_pred["잔차"], alpha=0.5, color='orange')
        ax_residual.axhline(0, color='gray', linestyle='--')
        ax_residual.set_xlabel("예측 LTV")
        ax_residual.set_ylabel("잔차 (실제 - 예측)")
        ax_residual.set_title("예측값에 따른 잔차 분포")
        st.pyplot(fig_residual)

        st.markdown("""
        #### 🔸 4. 예측값 대비 잔차 분석
        - 예측값이 커질수록 오차가 커지는 경향이 있다면 과대 예측 문제가 있을 수 있습니다.
        - 잔차가 불규칙하게 분포한다면 모델의 일반화 성능이 좋다고 볼 수 있습니다.
        - 잔차 분포가 특정 방향으로 편향되어 있으면 해당 구간의 재모델링이 필요할 수 있습니다.
        """)

    with col2:
        st.markdown("#### 👥 고객 등급별 평균 오차")
        if "고객 등급" in df_with_pred.columns:
            grade_error = df_with_pred.groupby("고객 등급")["잔차"].mean().reset_index()
            fig_grade, ax_grade = plt.subplots()
            ax_grade.bar(grade_error["고객 등급"], grade_error["잔차"], color='mediumseagreen')
            ax_grade.set_ylabel("평균 잔차")
            ax_grade.set_title("고객 등급별 평균 예측 오차")
            st.pyplot(fig_grade)

            st.markdown("""
            #### 🔸 5. 고객 등급별 오차 분석
            - VIP, 일반, 신규 고객군별로 예측 오차가 다르게 나타날 수 있습니다.
            - 특정 등급에서 예측 오차가 크다면 해당 그룹에 대해 별도의 모델링 또는 변수 조정이 필요합니다.
            - 등급별 예측 신뢰도를 기반으로 마케팅 전략도 차별화할 수 있습니다.
            """)
        else:
            st.warning("고객 등급 정보가 없어 등급별 분석을 생략합니다.")

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


    # 추가 추천 항목 생성 함수
    def get_recommendations(ltv):
        """검색 결과 [1]의 마케팅 전략 반영"""
        if ltv >= 80000000:  # 고가치 고객
            return {
                "차량": "제네시스-GV90-프레스티지",
                "금융": "할부 금리 2.9% (7년)", 
                "서비스": "5년 무상 유지보수 + 개인 전용 충전소 설치"
            }
        elif 40000000 <= ltv < 80000000:  # 중간 가치
            return {
                "차량": "현대-아이오닉6-디럭스",
                "금융": "리스료 3.5% (3년)",
                "서비스": "3년 무상 정비 + 연 2회 차량 디테일링"
            }
        else:  # 일반 고객
            return {
                "차량": "현대-아반떼-스마트",
                "금융": "카드 할부 5.9% (5년)",
                "서비스": "1년 무상 점검 + 보험료 10% 할인"
            }
        
    st.markdown("###  고객 맞춤 추천")
    
    if "연령대" in df_with_pred.columns and "거주 지역" in df_with_pred.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            selected_age = st.selectbox("연령대 선택", df_with_pred["연령대"].unique())
        with col2:
            selected_region = st.selectbox("거주 지역 선택", df_with_pred["거주 지역"].unique())

        recommended = df_with_pred[
            (df_with_pred["연령대"] == selected_age) &
            (df_with_pred["거주 지역"] == selected_region)
        ].sort_values("예측 LTV", ascending=False).head(5)

        # 추천 카드 스타일링
        st.markdown("""
        <style>
            .recommend-card {
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                background: #ffffff;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("####  맞춤형 추천 리스트")
        for idx, row in recommended.iterrows():
            rec = get_recommendations(row['예측 LTV'])
            st.markdown(f"""
            <div class="recommend-card">
                <div style="font-size:18px; color:#2A7FFF; margin-bottom:8px;">🏅 고객 {idx+1}</div>
                <table>
                    <tr><td>연령대</td><td><strong>{row['연령대']}</strong></td></tr>
                    <tr><td>거주지</td><td><strong>{row['거주 지역']}</strong></td></tr>
                    <tr><td>예측 LTV</td><td><strong>{row['예측 LTV']:,.0f}원</strong></td></tr>
                </table>
                <hr style="margin:10px 0;">
                🚗 <strong>추천 차량:</strong> {rec['차량']}<br>
                💳 <strong>금융 혜택:</strong> {rec['금융']}<br>
                🛠️ <strong>서비스 패키지:</strong> {rec['서비스']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ 연령대 또는 거주 지역 정보가 부족합니다.")

    #  🗂 원본 데이터 확인
    st.markdown("###  🗂 원본 데이터 확인")
    with st.expander(" 🗂 원본 데이터 확인"):
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