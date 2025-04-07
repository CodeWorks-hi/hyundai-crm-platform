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
                - **대상**: 현대카드로 차량 구매한 고객  
                - **혜택**: 현대카드 슈퍼콘서트 티켓 2매 증정  
                - **참여 방법**: 차량 구매 시 현대카드 사용
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
        st.caption("현대카드로 차량을 구매하면 슈퍼콘서트 티켓 2매 증정! 자동차와 함께 특별한 경험까지 함께 드립니다.")
        with st.expander("이벤트 - 상세보기"):
            st.markdown("""
                - **대상**: 현대카드로 차량 구매한 고객  
                - **혜택**: 현대카드 슈퍼콘서트 티켓 2매 증정  
                - **참여 방법**: 차량 구매 시 현대카드 사용
            """)
    with colc:
        st.image("images/event/event6.png", use_container_width=True)
        st.markdown("#### 현대 EV: FLEX 페이백 시즌")
        st.caption("현대카드로 차량을 구매하면 슈퍼콘서트 티켓 2매 증정! 자동차와 함께 특별한 경험까지 함께 드립니다.")
        with st.expander("이벤트 - 상세보기"):
            st.markdown("""
                - **대상**: 현대카드로 차량 구매한 고객  
                - **혜택**: 현대카드 슈퍼콘서트 티켓 2매 증정  
                - **참여 방법**: 차량 구매 시 현대카드 사용
            """)
    with cole:
        st.image("images/event/event7.png", use_container_width=True)
        st.markdown("#### 현대 Spring Go! 주유 걱정 없이 떠나봄")
        st.caption("현대카드로 차량을 구매하면 슈퍼콘서트 티켓 2매 증정! 자동차와 함께 특별한 경험까지 함께 드립니다.")
        with st.expander("이벤트 - 상세보기"):
            st.markdown("""
                - **대상**: 현대카드로 차량 구매한 고객  
                - **혜택**: 현대카드 슈퍼콘서트 티켓 2매 증정  
                - **참여 방법**: 차량 구매 시 현대카드 사용
            """)
    st.markdown("---")
    col11, col12, col13, col14, col15  = st.columns([2, 0.1, 2, 0.1, 2])
    with col12:
        pass
    with col14:
        pass

    def render_paginated_list(df, category_name, current_page_key):
        items_per_page = 5
        df = df[df["구분"] == category_name].sort_values(by="등록일", ascending=False).reset_index(drop=True)
        total_pages = math.ceil(len(df) / items_per_page)
        current_page = st.session_state.get(current_page_key, 1)

        start = (current_page - 1) * items_per_page
        end = start + items_per_page
        paginated_df = df.iloc[start:end]

        for _, row in paginated_df.iterrows():
            with st.expander(row["제목"]):
                st.markdown(row["내용"])

        if total_pages > 1:
            cols = st.columns(total_pages + 2)
            with cols[0]:
                if st.button("◀", key=f"{category_name}_prev") and current_page > 1:
                    st.session_state[current_page_key] = current_page - 1
                    st.rerun()
            for i in range(total_pages):
                with cols[i + 1]:
                    if st.button(str(i + 1), key=f"{category_name}_page_{i+1}"):
                        st.session_state[current_page_key] = i + 1
                        st.rerun()
            with cols[-1]:
                if st.button("▶", key=f"{category_name}_next") and current_page < total_pages:
                    st.session_state[current_page_key] = current_page + 1
                    st.rerun()


