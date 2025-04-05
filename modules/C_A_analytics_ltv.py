# 판매·수출 관리
    # LTV 모델 결과, 시장 트렌드, 예측 분석



import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random
from C_A_analytics_ltv_customer import ltv_customer_ui
from C_A_analytics_ltv_market import ltv_market_ui
from C_A_analytics_ltv_demand import ltv_demand_ui


def ltv_ui():

    # 탭 구성
    tab1, tab2, tab3= st.tabs([
          "LTV 분석","시장 트렌드", "수요 예측 "
    ])


    with tab1:
        
        ltv_customer_ui()       # LTV 모델 결과
    with tab2:
        
        ltv_market_ui()          # 시장 트렌드
    with tab3:

        ltv_demand_ui()           # 예측 분석


    # 페이지 제목
    st.write("고객 생애 가치 예측을 분석하는 페이지입니다.")
    st.write("LTV 모델 결과, 시장 트렌드, 예측 분석")
    # 페이지 설명
    st.markdown("""
        ###  1. LTV 모델 결과 (고객 생애 가치 예측)

        ** 개념 설명:**  
        LTV(Lifetime Value)는 고객이 기업과 거래를 시작한 시점부터 관계가 끝날 때까지 발생시킬 것으로 예상되는 총 수익입니다.  
        이 지표를 예측하면 어떤 고객이 장기적으로 더 높은 가치를 가질지 미리 파악할 수 있습니다.

        ** 적용 기술:**  
        - XGBoost, LightGBM, CatBoost 등 Gradient Boosting 계열 모델  
        - 주요 입력 변수:  
        - 구매 이력 (차종, 금액, 빈도)  
        - 방문/상담 이력 (딜러접촉, 앱/웹 사용)  
        - 금융 상품 사용 내역  
        - AS/서비스 이용 기록  

        ** 활용 예시:**

        | 고객명 | 최근 구매       | 누적 방문 수 | LTV 예측 (₩)  | 등급     |
        |--------|----------------|--------------|----------------|----------|
        | 김철수 | K5 하이브리드   | 7회          | 48,000,000     | ★★★★★   |
        | 박지민 | 쏘렌토          | 2회          | 15,000,000     | ★★☆☆☆   |

        > ☑️ 마케팅 우선순위, VIP 케어 서비스, 리스/보험 설계 등에 활용 가능

        ---

        ###  2. 시장 트렌드 분석

        **개념 설명:**  
        차량 소비 흐름, 차종별 인기 변화, 신흥 시장의 성장 추이 등을 정량적으로 분석하며,  
        지역/시기/고객 세그먼트를 기준으로 트렌드를 도출합니다.

        ** 예측 대상:**  
        - 친환경차 수요 증가 추세  
        - 지역별 인기 차종 변화 (예: 동남아 → SUV 선호 증가)  
        - 연령대별 구매 행태 변화 (MZ세대: 온라인 구매 전환 비율↑)

        ** 시각화 예시:**  
        - 연도별 전기차 비중 변화 (라인차트)  
        - 지역별 SUV vs 세단 선호도 (파이차트)  
        - 고객 연령대별 첫 구매 차종 트렌드 (히트맵)

        ---

        ###  3. 예측 분석

        ** 개념 설명:**  
        미래의 수요, 구매 전환율, 재방문 가능성 등을 시계열 또는 회귀 모델로 예측하여  
        공장 생산 계획, 캠페인 타이밍, 재고 확보 전략 등 전사적 의사결정에 활용됩니다.

        ** 적용 기술:**  
        - LSTM (Long Short-Term Memory) 기반 시계열 예측  
        - XGBoost / Prophet 등 트렌드 분석  
        - 고객 행동 예측에는 Sequence 기반 모델 (RNN / Transformer 등)

        ** 예시:**

        | 차종        | 월별 수요 예측 (2025.4~6) | 성장률 (%) |
        |-------------|----------------------------|-------------|
        | EV6         | 1,800 → 2,100              | +16.7%      |
        | 팰리세이드  | 2,000 → 1,750              | -12.5%      |

        > ☑️ 이를 통해 생산량 조정, 프로모션 배분 등 데이터 기반 의사결정 가능

        ---

        ### 종합 시나리오 예시

        > “LTV 예측을 통해 VIP로 분류된 고객군이 다음 분기 SUV 차량에 대한 수요를 주도할 것으로 예측됨.  
        해당 고객의 구매 주기가 평균 18개월임을 감안해, 3개월 내 SUV 맞춤 캠페인을 집중 배포.”

        ---

        ###  시각화 아이디어

        - LTV 분포 그래프 (박스 플롯)  
        -  시장 트렌드 워드 클라우드 (뉴스 기반)  
        -  수요 예측 대시보드 (차종/월별/지역별 애니메이션 차트)

        ---

        ###  참고 논문 및 자료

        1. *Predicting Customer Lifetime Value*, Journal of Marketing Analytics (IF 3.5)  
        2. *LTV modeling using machine learning*, Applied Soft Computing, 2023  
        3. *Forecasting car sales with LSTM*, Neural Computing and Applications, 2022 (IF 6.0)  
        4. 현대자동차 빅데이터 분석센터 기술백서
        """)

