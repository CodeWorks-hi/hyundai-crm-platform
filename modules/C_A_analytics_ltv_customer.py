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
from datetime import datetime 


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




# 데이터 전처리 및 모델 학습 함수 수정
def preprocess_and_train_model(df):
    df = df.drop(columns=["이름", "연락처", "브랜드", "모델명", "공장명"], errors="ignore")
    df = df.drop(columns=["트림명"], errors="ignore")

    # 재현성 보장을 위한 시드 설정
    np.random.seed(42)

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

    model = XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42,deterministic_histogram=True  # 결정적 히스토그램 활성화
    )

    model.fit(X_train, y_train)

    os.makedirs("model", exist_ok=True)
    model_version = datetime.now().strftime("%Y%m%d%H%M") 
    joblib.dump(model, f"model/xgb_model_v{model_version}.pkl")

    return model, df, X

# PDF 리포트 생성 함수 수정
def generate_pdf_report(df_top):
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont("Helvetica", 14)
    c.drawString(100, 800, f"LTV 예측 리포트 상위 {len(df_top)}명")

    y = 760
    for idx, row in df_top.iterrows():
        rank = idx + 1
        line = f"{rank}위: {row['연령대']} / {row['거주 지역']} / {row['예측 LTV']:,.0f}원"
        c.drawString(80, y, line)
        y -= 20
        if y < 100:
            break

    c.save()
    buffer.seek(0)
    return buffer

def ltv_customer_ui():
    # 데이터 로드
    df_customer, df_export, df_domestic, df_list = load_data()

    with st.spinner("모델 학습 및 예측 중..."):
        model, df_with_pred, X = preprocess_and_train_model(df_domestic)
        df_with_pred["예측 LTV"] = model.predict(X)

    # 상단 컬럼 레이아웃 추가

# 상단 컬럼 레이아웃 추가
    col_top_selector, _ = st.columns([7, 3])

    with col_top_selector:
    # 표시할 상위 고객 수 선택
        top_n = st.selectbox(
    "표시할 상위 고객 수",
        options=[10, 20, 50, 100],
        index=0,
        key="top_n_selector"
        )
    st.markdown("---")

    # 데이터프레임 인덱스 재설정
    top_n_df = df_with_pred.sort_values(by=["예측 LTV"], ascending=False).head(top_n).reset_index(drop=True)

    top_n_df.index += 1

    # 데이터프레임 표시
    st.dataframe(
        top_n_df[["연령대", "거주 지역", "예측 LTV", "고객 평생 가치"]]
        .style.format({'예측 LTV': '{:,.0f}원'}),
        height=400 if top_n <= 20 else 600
    )


    # PDF 리포트 생성 함수 수정
    def generate_pdf_report(df_top):
        buffer = BytesIO()
        c = canvas.Canvas(buffer)
        c.setFont("Helvetica", 14)
        c.drawString(100, 800, f"LTV 예측 리포트 상위 {len(df_top)}명")
        
        y = 760
        for idx, row in df_top.iterrows():
            rank = idx + 1
            line = f"{rank}위: {row['연령대']} / {row['거주 지역']} / {row['예측 LTV']:,.0f}원"
            c.drawString(80, y, line)
            y -= 20
            if y < 100:
                break
                
        c.save()
        buffer.seek(0)
        return buffer


    st.markdown("---")

    # 예측 결과 시각화
    st.markdown("#### 예측 결과 분석 및 시각화")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 🔹 예측 vs 실제 LTV 오차 분포")
        df_with_pred["LTV 오차"] = df_with_pred["고객 평생 가치"] - df_with_pred["예측 LTV"]
        fig1, ax1 = plt.subplots()
        ax1.hist(df_with_pred["LTV 오차"], bins=20, color='salmon', edgecolor='black')
        ax1.set_title("예측 오차 분포 (실제 - 예측)")
        ax1.set_xlabel("LTV 오차 (원)")
        ax1.set_ylabel("고객 수")
        st.pyplot(fig1)

        st.markdown("""
        ##### 🔸 1. 예측 오차 분포 분석
          - **오차란?**  
          예측 오차는 실제 LTV와 모델이 예측한 LTV 간의 차이를 의미합니다.  
          수학적으로는 다음과 같이 계산됩니다:  
          `오차 = 실제 LTV - 예측 LTV`
        - **분석 내용**  
          - 위의 히스토그램은 고객별 실제 LTV와 예측 LTV 간의 차이를 시각적으로 보여줍니다.  
          - 분포 중심이 0에 가까워질수록 모델이 전반적으로 정확하게 예측하고 있음을 의미합니다.  
          - 오차가 특정 방향으로 치우쳐 있다면, 특정 그룹에 대해 과소/과대 평가가 이루어졌을 가능성이 있습니다.
        - **활용 방안**  
          - 오차가 큰 구간을 식별하여 해당 고객 그룹에 대한 모델 개선 작업 수행.
          - 특정 고객 등급(VIP, 일반, 신규)에 따른 오차 패턴 분석을 통해 맞춤형 마케팅 전략 수립.
        """)


    with col2:
        st.markdown("##### 🔹 예측 vs 실제 LTV 비교 (상위 50명)")
        top20 = df_with_pred.sort_values("고객 평생 가치", ascending=False).head(50).reset_index()
        fig2, ax2 = plt.subplots()
        ax2.plot(top20.index, top20["고객 평생 가치"], label="실제 LTV", marker='o')
        ax2.plot(top20.index, top20["예측 LTV"], label="예측 LTV", marker='x')
        ax2.set_title("상위 50명 고객 LTV 비교")
        ax2.set_xlabel("고객 순위")
        ax2.set_ylabel("LTV (원)")
        ax2.legend()
        st.pyplot(fig2)

        st.markdown("""
        ##### 🔸 2. 상위 고객 50명 비교 분석
       - **상위 고객 분석 목적**  
          상위 고객은 높은 LTV를 가진 잠재적 가치가 큰 고객으로, 이들의 예측값과 실제값 간 차이를 분석함으로써 모델의 성능을 평가할 수 있습니다.
        - **분석 내용**  
          - 실선은 실제 LTV를, 점선은 모델이 예측한 LTV를 나타냅니다.  
          - 고객 순위가 높을수록(= 더 가치 있는 고객일수록), 예측값과 실제값 간 차이가 커질 가능성이 있습니다.  
          - 특히 상위 5~10명에서 예측값이 일관되게 낮거나 높다면, 해당 구간에 대한 모델 개선의 여지가 존재합니다.
        - **활용 방안**  
          - 상위 고객 그룹에 대한 모델 재학습 및 변수 조정을 통해 예측 정확도 향상.  
          - 상위 고객별 맞춤형 혜택 제공(예: VIP 금융 패키지, 프리미엄 서비스)을 통해 전환율 극대화.
        """)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#####  예측값에 따른 잔차 산점도 (잔차)")
        df_with_pred["잔차"] = df_with_pred["고객 평생 가치"] - df_with_pred["예측 LTV"]
        fig_residual, ax_residual = plt.subplots()
        ax_residual.scatter(df_with_pred["예측 LTV"], df_with_pred["잔차"], alpha=0.5, color='orange')
        ax_residual.axhline(0, color='gray', linestyle='--')
        ax_residual.set_xlabel("예측 LTV")
        ax_residual.set_ylabel("잔차 (실제 - 예측)")
        ax_residual.set_title("예측값에 따른 잔차 분포")
        st.pyplot(fig_residual)

        st.markdown("""
                ##### 🔸 4. 예측값 대비 잔차 분석
                - **잔차란?**  
                잔차는 실제값과 모델이 예측한 값의 차이를 의미합니다.  
                수학적으로는 다음과 같이 표현됩니다:  
                `잔차 = 실제값 - 예측값`
                - **분석 목적**  
                잔차를 분석하면 모델의 예측 정확도를 평가하고, 개선이 필요한 부분을 식별할 수 있습니다.
                - **주요 분석 내용**  
                - 예측값이 커질수록 오차가 커지는 경향이 있다면 과대 예측 문제가 있을 수 있습니다.
                - 잔차가 불규칙하게 분포한다면 모델의 일반화 성능이 좋다고 볼 수 있습니다.
                - 잔차 분포가 특정 방향으로 편향되어 있으면 해당 구간의 재모델링이 필요할 수 있습니다.
                """)
        
    with col2:
        st.markdown("#####  고객 등급별 평균 오차")
        if "고객 등급" in df_with_pred.columns:
            grade_error = df_with_pred.groupby("고객 등급")["잔차"].mean().reset_index()
            fig_grade, ax_grade = plt.subplots()
            ax_grade.bar(grade_error["고객 등급"], grade_error["잔차"], color='mediumseagreen')
            ax_grade.set_ylabel("평균 잔차")
            ax_grade.set_title("고객 등급별 평균 예측 오차")
            st.pyplot(fig_grade)


            st.markdown("""
                        
            ##### 🔸 5. 고객 등급별 오차 분석
            - **분석 목적**  
              - VIP 고객군에서 예측 오차가 크다면 고가 상품 및 프리미엄 서비스에 대한 모델 개선이 필요합니다.
              - 일반 고객군은 평균적인 구매 패턴을 반영하여 예측 모델을 최적화할 수 있습니다.
              - 신규 고객군은 데이터 부족으로 인해 발생하는 오차를 줄이기 위해 추가 변수 확보가 필요합니다.
            - **활용 방안**  
              - 등급별 예측 신뢰도를 기반으로 마케팅 전략을 차별화하여 전환율을 높일 수 있습니다.
              - VIP 고객군: 맞춤형 금융 혜택 및 컨시어지 서비스 제공
              - 일반 고객군: 대중적인 프로모션 및 장기 할부 옵션 제안
              - 신규 고객군: 초기 구매 유도 캠페인 및 데이터 확보를 위한 설문조사 진행
            """)

        else:
            st.warning("고객 등급 정보가 없어 등급별 분석을 생략합니다.")

    st.markdown("---")

    # PDF 리포트 생성
    pdf_buffer = generate_pdf_report(top_n_df)

    # 다운로드 버튼
    st.download_button(
        label="📥 LTV 예측 리포트 다운로드",
        data=pdf_buffer,
        file_name=f"ltv_report_top_{top_n}.pdf",
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