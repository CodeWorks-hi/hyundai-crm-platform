# 판매·수출 관리
    # 마케팅 캠페인/ # 캠페인 성과 측정
        # 경제 지표 기반 마케팅 전략 표시


import streamlit as st
import pandas as pd


# 경제 지표 기반 마케팅 전략 표시
def marketing_strategies_ui():
    st.markdown("## 🎯 경제 지표 기반 마케팅 캠페인 전략 10선: 현대기아 CRM 사례")
    
    # 1. 금리/환율/뉴스심리지수 기반 반응률 예측
    with st.expander(" 금리/환율/뉴스심리지수 기반 반응률 예측", expanded=True):
        st.markdown("""
        **🔍 전략적 배경**  
        - 소비자 신뢰지수(CCI) 71.1(2025.1 기준) 리세션 수준 대응  
        - FRED 경제데이터 API 연동 실시간 모니터링 시스템 구축

        **🚀 실행 방안**  
        ```
        # 경제지표 트리거 조건
        if (interest_rate < 3.0) & (exchange_rate > 1300):
            activate_campaign('환율헤지_프로모션')
        ```
        **📈 성과 사례**  
        - 2024년 4월 환율 1,300원 돌파 시 전환율 22% 상승
        """)
        
    # 2. 경기 회복기 리타겟팅 캠페인
    with st.expander(" 경기 회복기 리타겟팅 캠페인", expanded=False):
        st.markdown("""
        **📊 데이터 활용**  
        ```
        # AI 예측 모델
        model.predict(consumer_index).when(
            lambda x: x > 75, 
            send_retargeting(segment='침체기_미구매자')
        )
        ```
        **📌 실행 사례**  
        - 2024년 1분기 ROI 4.8배 달성
        """)

    # 3. 소비자심리지수 하락기 프로모션
    with st.markdown("### 소비자심리지수 대응 전략"):
        col1, col2 = st.columns([3,2])
        with col1:
            st.code("""
            # 자동화 발송 로직
            if consumer_index < 75:
                send_campaign(
                    title="경제 불확실성 대비 특별 할인",
                    targets=price_sensitive_users
                )
            """, language='python')
        with col2:
            st.metric("2025년 1월 성과", "주문량 41% 증가", "+18%")

    # 4. EV 타겟 혜택 강화
    st.markdown("---")
    st.markdown("###  EV 충전 인프라 연계 전략")
    st.image("https://example.com/ev_charging_map.jpg", width=650)
    st.caption("전기차 충전소 위치 기반 타겟팅 시스템")

    # 5. 유지비 절감 캠페인
    st.markdown("###  유지비 계산기 통합 전략")
    with st.container(border=True):
        st.markdown("**실시간 유가 연동 시스템**")
        st.progress(65, text="하이브리드 차량 추천 비중: 55%")
        st.write("국제유가 변동 시 자동 추천 알고리즘 가동")

    # 종합 로드맵 표시
    st.markdown("---")
    st.markdown("###  종합 실행 로드맵")
    roadmap_data = pd.DataFrame([
        ["1Q", "경제지표 모니터링 시스템", "≤1h 데이터 수집 주기"],
        ["2Q", "EV 충전 인프라 확대", "500개소 제휴처"],
        ["3Q", "AI 유지비 계산기", "80%+ 사용률"],
        ["4Q", "역사적 데이터 모델", "92% 정확도"]
    ], columns=["단계", "실행 내용", "측정 지표"])
    
    st.dataframe(
        roadmap_data,
        column_config={
            "단계": st.column_config.TextColumn(width="small"),
            "측정 지표": st.column_config.ProgressColumn(
                width="medium",
                format="%f",
                min_value=0,
                max_value=100
            )
        },
        hide_index=True,
        use_container_width=True
    )

