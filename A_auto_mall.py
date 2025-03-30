# A_auto_mall.py

import streamlit as st

def app():
    st.title("딜러가 고객이 왔을때 차량 목록 보여주기, 고객정보입력하기, 차량 선택 해서 판매 할 경우 판매 등록, 상담내용등록, 고객 성향 파악 , 고객에게 맞춤 차량 추천 ")
    st.markdown("차량 구매, 등록, 조회 등의 기능 제공")
    tabs = st.tabs([
        "대시보드 개요",
        "판매 실적 현황",
        "차량 재고 현황",
        "생산 계획 관리",
        "AI 수요 예측",
        "고객 맞춤 추천",
        "온라인 구매 요청 관리"
    ])

    with tabs[0]:
        st.write("00 화면입니다. (대시보드 개요)")

    with tabs[1]:
        st.write("00 화면입니다. (판매 실적 현황)")

    with tabs[2]:
        st.write("00 화면입니다. (차량 재고 현황)")

    with tabs[3]:
        st.write("00 화면입니다. (생산 계획 관리)")

    with tabs[4]:
        st.write("00 화면입니다. (AI 수요 예측)")

    with tabs[5]:
        st.write("00 화면입니다. (고객 맞춤 추천)")

    with tabs[6]:
        st.write("00 화면입니다. (온라인 구매 요청 관리)")
        
    if st.button("← 메인으로 돌아가기"):
        st.session_state.current_page = "home"
        st.rerun()
