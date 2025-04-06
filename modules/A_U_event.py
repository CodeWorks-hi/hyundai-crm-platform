import pandas as pd  # 예: 이벤트 로그 저장 시
import datetime       # 예: 이벤트 시작일/종료일 표시 시
import streamlit as st

def event_ui():
    # 상단 배너 스타일
    st.markdown("""
        <div style="background-color: #f4f0ec; padding: 60px 0; text-align: center;">
            <h1 style="font-size: 48px; font-weight: bold; margin-bottom: 12px;">이벤트</h1>
            <p style="font-size: 18px;">고객님을 위한 스페셜 이벤트는 계속됩니다. 즐거운 행운과 경품을 만나보세요!</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### 진행 중인 이벤트")

    col4, col1, col2, col3, col5  = st.columns([0.1, 1, 0.1, 1, 0.1])
    with col4:
        pass
    with col5:
        pass
    with col1:
        st.image("https://www.nanamcom.co.kr/news/photo/202403/7630_19015_5241.png", use_container_width=True)
        st.markdown("#### 현대카 클럽 프로그램")
        with st.expander("📌 프로그램 안내"):
            st.markdown(
                """
                - **할부 개월**: 60개월  
                - **이용 조건**: 50개월 이상 이용 후 기존 차량 반납  
                - **보상 혜택**:
                    - 중고차 시세 보상
                    - 신차 구매 시 구매금액의 **10% 지원**
                - **특징**: 갤럭시클럽 방식의 차량 구매 프로그램
                """
            )
        st.button("자세히 보기", use_container_width=True, key="event_button_1")
    with col2:
        pass
    with col3:
        st.image("https://cdn.fnnews21.com/news/photo/201306/6165_5290_3630.jpg", use_container_width=True)
        st.markdown("#### 현대카드 제휴 이벤트")
        with st.expander("📌 혜택 상세"):
            st.markdown(
                """
                - **대상**: 현대카드로 차량 구매한 고객  
                - **혜택**: 현대카드 슈퍼콘서트 티켓 2매 증정  
                - **참여 방법**: 차량 구매 시 현대카드 사용
                """
            )
        st.button("자세히 보기", use_container_width=True, key="event_button_2")

    st.markdown("---")
    st.markdown("✅ 더 많은 이벤트는 현대자동차 홈페이지에서 확인하세요.")
    st.markdown("[현대차 이벤트 페이지 바로가기](https://www.hyundai.com/kr/ko/event)")
