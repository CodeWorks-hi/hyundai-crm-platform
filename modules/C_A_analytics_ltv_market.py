# 판매·수출 관리
    # LTV 모델 결과, 시장 트렌드, 예측 분석
        # 시장 트렌드


import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import OneHotEncoder


def preprocess_for_prediction(df):
    # 예측에 필요 없는 정보만 제거
    drop_cols = [
        '연번', '이름', '생년월일', '휴대폰 번호', '이메일', '아이디',
        '가입일', '주소', '고객 평생 가치'  # 예측 대상 포함
    ]
    df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')

    # 결측값 제거 (모델 학습 시에도 적용했다면 동일하게 적용)
    df = df.dropna()

    # 범주형 변수 인코딩
    df = pd.get_dummies(df)

    return df

def ltv_market_ui():

    df = pd.read_csv("data/export_customer_data.csv")

    # 연령대별 평균 LTV 시각화
    fig1 = px.bar(df.groupby("연령대")["고객 평생 가치"].mean().reset_index(),
                  x="연령대", y="고객 평생 가치", title="연령대별 평균 고객 생애 가치")
    st.plotly_chart(fig1, use_container_width=True)

    # 차량 유형별 LTV
    if "최근 구매 제품" in df.columns:
        fig = px.box(df, x="최근 구매 제품", y="고객 평생 가치", title="차량 유형별 고객 가치 분포")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("최근 구매 제품 데이터가 포함되어 있지 않습니다.")

    # 등급별 평균 LTV
    fig3 = px.bar(df.groupby("고객 등급")["고객 평생 가치"].mean().reset_index(),
                  x="고객 등급", y="고객 평생 가치", title="고객 등급별 평균 LTV")
    st.plotly_chart(fig3, use_container_width=True)

        # ====================== 신규 추가된 트렌드 분석 섹션 ======================
    st.markdown("""
    <style>
        .trend-header { 
            color: #2A7FFF; 
            font-size: 24px; 
            border-bottom: 3px solid #2A7FFF;
            padding-bottom: 5px;
            margin: 30px 0 20px 0;
        }
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
        .trend-icon { 
            font-size: 24px; 
            margin-right: 10px; 
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="trend-header">📈 시장 트렌드 분석</div>', unsafe_allow_html=True)
    
    # 트렌드 1: 전기차 시장 성장
    st.markdown('''
    <div class="trend-card">
        <div class="trend-title">
            <span class="trend-icon">🔋</span>
            <span>전기차 시장 폭발적 성장</span>
        </div>
        <ul style="color:#333;">
            <li>2025년 글로벌 전기차 시장 점유율 <b>35%</b> 예상 (2030년 65% 전망)</li>
            <li>국내 판매량 전년 대비 <span style="color:#2A7FFF;">+78%</span> 증가</li>
            <li>주요 성장 동력: 배터리 기술 발전, 충전 인프라 확대</li>
        </ul>
    </div>
    ''', unsafe_allow_html=True)

    # 트렌드 2: 자율주행 기술
    st.markdown('''
    <div class="trend-card">
        <div class="trend-title">
            <span class="trend-icon">🤖</span>
            <span>자율주행 기술 상용화 가속</span>
        </div>
        <ul style="color:#333;">
            <li>L3 자율주행 차량 시장 규모 <b>연평균 42%</b> 성장 예상</li>
            <li>우리사 매출 대비 R&D 투자 비중 <span style="color:#2A7FFF;">15% → 22%</span> 확대</li>
            <li>핵심 기술: AI 기반 경로 예측 시스템, 실시간 도로정보 처리</li>
        </ul>
    </div>
    ''', unsafe_allow_html=True)

    # 트렌드 3: 지속가능성 강화
    st.markdown('''
    <div class="trend-card">
        <div class="trend-title">
            <span class="trend-icon">🌱</span>
            <span>친환경 소재 수요 증가</span>
        </div>
        <ul style="color:#333;">
            <li>재활용 소재 사용률 <b>2025년 45%</b> 목표 (현재 28%)</li>
            <li>배터리 재활용 시스템 구축: 수명 주기 연장 기술 개발 중</li>
            <li>신규 모델 CO2 배출량 <span style="color:#2A7FFF;">-35%</span> 달성</li>
        </ul>
    </div>
    ''', unsafe_allow_html=True)

    # ====================== 기존 차트 섹션 수정 ======================
    st.markdown("---")
    st.subheader("📊 생산 현황 심층 분석")
    
    col1, col2 = st.columns([2,1])
    with col1:
        # 생산량 예측 대시보드
        st.markdown("### 🎯 목표 대비 생산량")
        target_data = pd.DataFrame({
            '카테고리': ['전기차', 'SUV', '세단', '화물차'],
            '목표량': [12000, 8500, 6500, 3000],
            '실적': [11000, 9200, 6000, 2800]
        })
        fig = px.bar(target_data, 
                    x='카테고리', 
                    y=['목표량', '실적'], 
                    barmode='group',
                    color_discrete_sequence=['#2A7FFF', '#00C2FF'])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # 실시간 생산 지표
        st.markdown("### ⚡ 실시간 생산 지표")
        st.metric("금일 생산량", "3,420대", "+8.2% vs 전일")
        st.metric("설비 가동률", "92.4%", "최적 상태 유지")
        st.metric("불량률", "0.23%", "-0.07% 개선", delta_color="inverse")
