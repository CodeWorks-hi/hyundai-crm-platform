import streamlit as st
from .C_admin_analytics_sales import analytics_sales_ui
from .C_admin_analytics_ltv import analytics_ltv_ui
from .C_admin_analytics_marketing import analytics_marketing_ui
from .C_admin_analytics_economy import analytics_economy_ui

def admin_analytics_ui():
    st.markdown("""
        <style>
            div[data-baseweb="tabs"] > div {
                background-color: #fff;
                padding: 0.5rem 1rem;
            }
            div[data-baseweb="tab"] {
                font-weight: 500;
                color: #666;
            }
            div[data-baseweb="tab"][aria-selected="true"] {
                border-bottom: 3px solid red;
                color: black !important;
                font-weight: 700;
            }
        </style>
    """, unsafe_allow_html=True)

    tab_names = [
        "국내/해외 판매 관리",
        "LTV 및 시장 예측 분석",
        "마케팅 캠페인 성과",
        "글로벌 경제 인사이트내"
    ]

    selected_tab = st.tabs(tab_names)

    with selected_tab[0]:
        analytics_sales_ui()

    with selected_tab[1]:
        analytics_ltv_ui()

    with selected_tab[2]:
        analytics_marketing_ui()

    with selected_tab[3]:
        analytics_economy_ui()


