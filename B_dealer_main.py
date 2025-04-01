# 예: B_dealer_hub.py
import streamlit as st

from modules.B_dealer_dashboard import dashboard_ui

def app():
    st.title("딜러 페이지")
    tabs = st.tabs([
        "딜러 대시보드",
        "고객 360도 뷰", 
        "재고 현황", 
        "리드 관리", 
        "판매 등록",
        "AI 수요 예측",
        "서비스 일정", 
        "판매 인텔리전스"
    ])

    tab_modules = [
        ("modules.B_dealer_dashboard", "dashboard_ui"),
        ("modules.B_dealer_customers", "customers_ui"),                     # 고객 360도 뷰, LTV 점수, 추천 액션
        ("modules.B_dealer_inventory", "inventory_ui"),                     # 재고 현황, 발주 추천, 마진 분석
        ("modules.B_dealer_leads", "leads_ui"),                             # 리드 퍼널, 스코어링, 자동 팔로업
        ("modules.B_dealer_registration", "sales_registration_ui"),         # 판매 등록
        ("modules.B_ealer_demand_forecast", "demand_forecast_ui"),           # AI 수요 예측
        ("modules.B_dealer_service", "demand_forecast_ui"),                 # 서비스 일정, 고객 충성도 관리
        ("modules.B_dealer_eco", "dealer_eco_ui")                           # 경제 지표 기반 판매 인텔리전스, 금융 상품 최적화
    ]

    with tabs[0]:
        dashboard_ui()

    with tabs[1]:
        st.write("가안.")

    with tabs[2]:
        st.write("재고 현황")

    with tabs[3]:
        st.write("리드 관리")

    with tabs[4]:
        st.write("판매 등록")

    with tabs[5]:
        st.write("AI 수요 예측")

    with tabs[6]:
        st.write("서비스 일정")

    with tabs[7]:
        st.write("판매 인텔리전스")


    # ✔ 안전한 방식: 세션 상태로 페이지 전환
    if st.button("← 메인으로 돌아가기"):
        st.session_state.current_page = "home"
        st.rerun()

