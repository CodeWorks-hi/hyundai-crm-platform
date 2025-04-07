import pandas as pd  # 예: 이벤트 로그 저장 시
import datetime       # 예: 이벤트 시작일/종료일 표시 시
import streamlit as st
import math

def event_ui():
    # 상단 배너 스타일
    st.markdown("""
        <div style="background-color: #f4f0ec; padding: 60px 0; text-align: center;">
            <h1 style="font-size: 48px; font-weight: bold; margin-bottom: 12px;">이벤트</h1>
            <p style="font-size: 18px;">고객님을 위한 스페셜 이벤트는 계속됩니다. 즐거운 행운과 경품을 만나보세요!</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("")
    st.markdown("---")

    col4, col1, col2, col3, col5  = st.columns([0.1, 1, 0.1, 1, 0.1])
    with col4:
        pass
    with col5:
        pass
    with col1:
        st.image("images/event/event4.png", use_container_width=True)
        st.markdown("#### 현대카 클럽 프로그램")
        st.caption("장기 이용 고객을 위한 프리미엄 프로그램! 50개월 이상 사용 후 차량 반납 시 중고차 시세 보상과 신차 구매금액의 5%를 지원해드립니다.")
        with st.expander("프로그램 - 상세보기"):
            st.markdown("""
                - **할부 개월**: 60개월  
                - **이용 조건**: 50개월 이상 이용 후 기존 차량 반납  
                - **보상 혜택**:
                    - 중고차 시세 보상
                    - 신차 구매 시 구매금액의 **5% 지원**
                - **특징**: 갤럭시클럽 방식의 차량 구매 프로그램
            """)
    with col2:
        pass

    with col3:
        st.image("images/event/event3.jpg", use_container_width=True)
        st.markdown("#### 현대카드 제휴 이벤트")
        st.caption("현대카드로 차량을 구매하면 슈퍼콘서트 티켓 2매 증정! 자동차와 함께 특별한 경험까지 함께 드립니다.")

        with st.expander("이벤트 - 상세보기"):
            st.markdown("""
        - **대상**: 현대카드로 차량을 구매한 고객  
        - **혜택**: **현대카드 슈퍼콘서트 티켓 2매 증정**  
        - **참여 방법**: 차량 계약 시 현대카드 결제 진행 → 자동 응모  
        - **유의사항**: 티켓은 선착순 한정 / 일부 차종 제외 가능
            """)
    st.markdown("---")
    cola, colb, colc, cold, cole  = st.columns([2, 0.1, 2, 0.1, 2])
    with colb:
        pass
    with cold:
        pass
    with cola:
        st.image("images/event/event5.png", use_container_width=True)
        st.markdown("#### 현대 Spring Go! 주유 걱정 없이 떠나봄")
        st.caption("봄바람 타고 떠나는 드라이브, 유류비 걱정은 현대가 책임질게요!")
        with st.expander("이벤트 - 상세보기"):
            st.markdown("""
        - **대상**: 2025년 4~5월 현대차 출고 고객  
        - **혜택**: 최대 30만원 상당 주유권 또는 전기차 충전 크레딧 제공  
        - **참여 방법**: 이벤트 대상 차종 계약 및 출고 시 자동 응모  
        - **보너스**: SNS 인증샷 이벤트 참여 시 캠핑용품 등 경품 추첨 제공  
        - **추가 서비스**: 봄철 무상 차량 점검 프로그램 운영
            """)
    with colc:
        st.image("images/event/event6.png", use_container_width=True)
        st.markdown("#### Enjoy Car Camping with Hyundai")
        st.caption("캠핑의 계절, SUV와 함께 자연으로 떠나세요. 지금 구매 시 특별한 혜택을 드립니다.")

        with st.expander("이벤트 - 상세보기"):
            st.markdown("""
        - **대상**: 2025년 4~5월 중 현대 SUV 차량 구매 고객  
        - **혜택**: 100만원 상당 **프리미엄 캠핑용품 세트** 증정  
        - **참여 방법**: 이벤트 대상 SUV 차량 계약 및 출고 시 자동 참여  
        - **추가 혜택**:  
            - 캠핑 인증샷 SNS 업로드 시 **추가 경품 이벤트** 참여 가능  
            - 출고 고객 대상 **무상 차량 점검 서비스** 제공
            """)
    with cole:
        st.image("images/event/event7.png", use_container_width=True)
        st.markdown("#### 현대자동차 봄맞이 주행 지원 이벤트")
        st.caption("따뜻한 봄날, 가볍게 시승하고 주유 상품권 혜택까지 받아가세요!")

        with st.expander("이벤트 - 상세보기"):
            st.markdown("""
        - **대상**: 현대차 시승 프로그램에 참여한 고객  
        - **혜택**: **주유 상품권 제공**  
        - **참여 방법**: 전국 현대자동차 전시장에서 시승 예약 후 참여  
        - **이벤트 기간**: 2024년 4월 15일 ~ 2024년 5월 14일  
        - **유의 사항**: 일부 전시장 제외 / 상품권은 한정 수량 소진 시까지 제공
            """)
