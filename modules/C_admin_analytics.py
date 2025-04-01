# 판매·수출 모니터링 



import streamlit as st

# 하위 모듈 임포트
from .C_admin_analytics_sales import analytics_sales_ui
from .C_admin_analytics_ltv import analytics_ltv_ui
from .C_admin_analytics_marketing import analytics_marketing_ui
from .C_admin_analytics_economy import analytics_economy_ui


def admin_analytics_ui():
    st.title("판매·수출 모니터링")

    tab1, tab2, tab3, tab4 = st.tabs([
        "판매 및 수출 관리",
        "LTV 및 시장 예측 분석",
        "마케팅 캠페인 성과",
        "글로벌 경제 인사이트"
    ])

    with tab1:
        analytics_sales_ui()

    with tab2:
        analytics_ltv_ui()

    with tab3:
        analytics_marketing_ui()

    with tab4:
        analytics_economy_ui()

    st.markdown("---")
    if st.button("← 관리자 포털로 돌아가기"):
        st.switch_page("C_admin_main.py")