import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
from sklearn.preprocessing import OneHotEncoder

# 데이터 로드
@st.cache_data
def load_data():
    df_customer = pd.read_csv("data/customer_data.csv")
    df_export = pd.read_csv("data/export_customer_data.csv")
    df_domestic = pd.read_csv("data/domestic_customer_data.csv")
    return df_customer, df_export, df_domestic

# 모델 로드
try:
    domestic_model = joblib.load("model/xgb_domestic_ltv_model.pkl")
    export_model = joblib.load("model/xgb_export_ltv_model.pkl")
except Exception as e:
    st.error(f"모델 로드 오류: {e}")

# 데이터 전처리
def preprocess_data(df):
    # 실제 데이터 컬럼명 확인
    print("데이터 컬럼 목록:", df.columns.tolist())
    
    # 컬럼명 매핑 (실제 데이터에 맞게 수정)
    column_mapping = {
        '구매일자': 'order_date',  # 예시: 실제 컬럼명이 'order_date'인 경우
        '지역': 'region',
        '차종': 'car_type'
    }
    
    try:
        # 컬럼명 변경
        df = df.rename(columns=column_mapping)
        
        # 필수 컬럼 존재 여부 확인
        required_columns = ['order_date', 'region', 'car_type']
        for col in required_columns:
            if col not in df.columns:
                raise KeyError(f"필수 컬럼 '{col}'가 데이터에 존재하지 않습니다")

        # 전처리 로직
        df = df.drop(columns=['고객ID', '이름', '휴대폰번호'], errors='ignore')
        df['구매연도'] = pd.to_datetime(df['order_date']).dt.year
        df = pd.get_dummies(df, columns=['region', 'car_type'])
        
        return df

    except KeyError as e:
        st.error(f"데이터 오류: {str(e)}")
        st.stop()


# 시장 트렌드 섹션
def market_trend_section():
    st.markdown("""
    <style>
        .trend-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 25px;
        }
        .trend-title { 
            font-size: 20px; 
            color: #1a1a1a; 
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }
    </style>
    """, unsafe_allow_html=True)

    # 트렌드 카드
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="trend-card">
                <div class="trend-title">🔋 전기차 시장 성장</div>
                <div>• 2025년 점유율 35% 예상</div>
                <div>• 국내 판매량 +78%</div>
                <div>• 충전소 2,300개 설치</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="trend-card">
                <div class="trend-title">🤖 자율주행 기술</div>
                <div>• L3 시장 연성장 42%</div>
                <div>• R&D 투자 22%</div>
                <div>• 안전사고 -35%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="trend-card">
                <div class="trend-title">🌱 친환경 소재</div>
                <div>• 재활용률 45% 목표</div>
                <div>• CO2 배출 -35%</div>
                <div>• 배터리 수명 +40%</div>
            </div>
            """, unsafe_allow_html=True)

# 메인 대시보드
def ltv_market_ui():

    
    # 데이터 로드
    df_customer, df_export, df_domestic = load_data()
    
    # 전처리
    df_customer_clean = preprocess_data(df_customer)
    df_export_clean = preprocess_data(df_export)

    # 사이드바 필터
    with st.sidebar:
        st.header("분석 필터")
        selected_year = st.selectbox("연도 선택", options=df_customer_clean['구매연도'].unique())
        selected_region = st.multiselect("지역 선택", options=df_customer_clean['지역'].unique())

    # 대시보드 헤더
    st.title("🚗 자동차 시장 분석 & 예측 대시보드")
    
    
    # 주요 지표
    st.subheader("📊 실시간 생산 지표")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("금일 생산량", "3,420대", "+8.2%")
    col2.metric("설비 가동률", "92.4%", "최적 상태")
    col3.metric("불량률", "0.23%", "-0.07%")
    col4.metric("예측 수요량", "2,150대", "향후 30일")
    
    # 생산 분석 섹션
    st.markdown("---")
    st.subheader("🔍 생산 현황 심층 분석")
    
    # 생산량 예측 차트
    fig1 = px.line(df_domestic.groupby('월')['생산량'].sum().reset_index(),
                  x='월', y='생산량', title="월별 생산량 추이")
    st.plotly_chart(fig1, use_container_width=True)
    
    # 재고 분석
    st.subheader("📦 부품 재고 현황")
    col5, col6 = st.columns([2,1])
    
    with col5:
        fig2 = px.bar(df_domestic.sort_values('재고량', ascending=False).head(10),
                     x='부품명', y='재고량', color='공장명',
                     title="부품별 재고 현황")
        st.plotly_chart(fig2, use_container_width=True)
    
    with col6:
        st.dataframe(
            df_domestic[['부품명', '공장명', '재고량', '안전재고량']]
            .sort_values('재고량', ascending=False)
            .style.applymap(lambda x: 'color: red' if x < 200 else '', subset=['재고량']),
            height=400
        )

    # LTV 예측 섹션
    st.markdown("---")
    st.subheader("💰 고객 생애 가치(LTV) 예측")
    
    # 예측 입력 폼
    with st.form("ltv_prediction"):
        age = st.number_input("고객 연령", min_value=18, max_value=80)
        purchase_history = st.number_input("누적 구매 횟수", min_value=1)
        avg_spending = st.number_input("평균 구매 금액(만원)", min_value=1000)
        submitted = st.form_submit_button("예측 실행")
        
        if submitted:
            prediction = domestic_model.predict([[age, purchase_history, avg_spending]])
            st.success(f"예상 LTV: {prediction[0]:,.0f} 만원")


