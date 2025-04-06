import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
from sklearn.preprocessing import OneHotEncoder

# 데이터 컬럼 매핑 (검색 결과 [5] 반영)
COLUMN_MAPPINGS = {
    'customer': {
        '최근 구매 날짜': 'purchase_date',
        '거주 지역': 'region',
        '차량 유형': 'vehicle_type',
        '고객 평생 가치': 'ltv'
    },
    'export': {
        '최근 구매 날짜': 'purchase_date',
        '차량 구매 횟수': 'purchase_count',
        '고객 평생 가치': 'ltv'
    },
    'domestic': {
        '브랜드': 'brand',
        '모델명': 'model',
        '기본가격': 'price',
        '공장명': 'factory'  
    }
}

# 수정된 필수 컬럼 검증 로직
required_columns = {
    'customer': ['purchase_date', 'region', 'vehicle_type', 'ltv'],
    'export': ['purchase_date', 'purchase_count', 'ltv'],
    'domestic': ['brand', 'model', 'price', 'factory']  # 국내 데이터에만 factory 필수
}


# 데이터 로드
@st.cache_data
def load_data():
    try:
        # 실제 데이터 구조에 맞게 컬럼명 매핑 적용
        df_customer = pd.read_csv("data/customer_data.csv").rename(columns=COLUMN_MAPPINGS['customer'])
        df_export = pd.read_csv("data/export_customer_data.csv").rename(columns=COLUMN_MAPPINGS['export'])
        df_domestic = pd.read_csv("data/domestic_customer_data.csv").rename(columns=COLUMN_MAPPINGS['domestic'])
        
        return df_customer, df_export, df_domestic
    except Exception as e:
        st.error(f"데이터 로드 오류: {str(e)}")
        st.stop()

# 데이터 전처리
def preprocess_data(df, data_type):
    try:
        mapping = COLUMN_MAPPINGS[data_type]
        req_cols = required_columns[data_type]  # 데이터 타입별 필수 컬럼 사용
        
        # 필수 컬럼 검증
        missing = [col for col in req_cols if col not in df.columns]
        if missing:
            raise KeyError(f"필수 컬럼 누락: {missing}")
        

        # 공통 전처리
        if 'purchase_date' in df.columns:
            df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')
            df['구매연도'] = df['purchase_date'].dt.year

        # 데이터 타입별 추가 처리
        if data_type == 'customer':
            df = df.drop(columns=['연번','이름','생년월일','휴대폰 번호','이메일'], errors='ignore')
            df = pd.get_dummies(df, columns=['region', 'vehicle_type'])
            
        elif data_type == 'export':
            df = df.drop(columns=['연번','이름','성별'], errors='ignore')
            df = pd.get_dummies(df, columns=['purchase_count'])
            
        elif data_type == 'domestic':
            df = df.drop(columns=['이름','성별','연락처'], errors='ignore')
            df = pd.get_dummies(df, columns=['brand','model'])
            
        return df.dropna()

    except Exception as e:
        st.error(f"전처리 오류 ({data_type}): {str(e)}")
        st.stop()

# 시장 트렌드 섹션 (검색 결과 [4] 반영)
def market_trend_section():
    st.markdown("""
    <style>
        .trend-card {
            background: #f8f9fa;
            border-left: 4px solid #2A7FFF;
            padding: 1.5rem;
            margin: 1rem 0;
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    trends = [
        (" 전기차 트렌드", ["2025년 점유율 35%", "국내 판매량 +78%", "충전소 2,300개"]),
        (" 자율주행 기술", ["L3 시장 성장률 42%", "R&D 투자 22%", "사고율 -35%"]),
        (" 지속가능성", ["재활용률 45% 목표", "CO2 배출 -35%", "배터리 수명 +40%"])
    ]

    for idx, (title, items) in enumerate(trends):
        with cols[idx]:
            st.markdown(f"""
            <div class="trend-card">
                <h4>{title}</h4>
                <ul style='margin:0;padding-left:1.2rem'>
                    {''.join([f'<li>{item}</li>' for item in items])}
                </ul>
            </div>
            """, unsafe_allow_html=True)

# 메인 대시보드
def ltv_market_ui():
    df_customer, df_export, df_domestic = load_data()
    
    # 데이터 전처리
    df_customer_clean = preprocess_data(df_customer, 'customer')
    df_export_clean = preprocess_data(df_export, 'export')
    df_domestic_clean = preprocess_data(df_domestic, 'domestic')

    # 대시보드 레이아웃
    st.title("현대자동차 시장 분석 대시보드")
    
    # 상단 필터 섹션
    filter_container = st.container()
    with filter_container:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            selected_year = st.selectbox(
                "분석 연도 선택",
                options=sorted(df_customer_clean['구매연도'].unique(), reverse=True),
                index=0
            )
            
        with col2:
            factories = df_domestic_clean['factory'].unique().tolist()
            selected_factories = st.multiselect(
                " 공장 선택",
                options=factories,
                default=factories[:2]
            )

    market_trend_section()

    # 실시간 지표
    cols = st.columns(4)
    metrics = [
        ("3,420대", "금일 생산량", "+8.2%"),
        ("92.4%", "설비 가동률", "최적 상태"),
        ("0.23%", "불량률", "-0.07%"),
        ("2,150대", "예측 수요량", "향후 30일")
    ]
    
    # 생산 분석 섹션
    st.markdown(" ###  생산 현황 분석")
    
    # 월별 생산량 차트 (필터 적용)
    filtered_data = df_domestic_clean[
        (df_domestic_clean['factory'].isin(selected_factories)) &
        (df_domestic_clean['구매연도'] == selected_year)
    ]
    
    fig1 = px.line(
        filtered_data,
        x='구매연도',
        y='price',
        color='factory',
        labels={'price': '생산 금액(억 원)', '구매연도': '연도'},
        title=f"{selected_year}년 공장별 생산 추이"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # LTV 분석 (필터 적용)
    st.markdown(" ###  고객 생애 가치 분석")

    col1, col2 = st.columns([2, 1])
    with col1:
        # 국내 생산 데이터 사용
        fig2 = px.box(
            df_domestic_clean,  # domestic 데이터 사용
            x='factory',
            y='price',
            color='brand',
            title="공장별 가격 분포",
            labels={'price': '가격(만 원)', 'factory': '공장'}
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.dataframe(
            df_domestic_clean.groupby(['factory','brand'])['price'].mean()
            .unstack().style.format("{:,.0f}만 원"),
            height=400
        )

