import streamlit as st
from .C_A_analytics_sales import sales_ui
from .C_A_analytics_ltv import ltv_ui
from .C_A_analytics_marketing import marketing_ui
from .C_A_analytics_economy import economy_ui

def analytics_ui():
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
        "글로벌 경제 인사이트내",
        "마케팅 캠페인 성과"

    ]

    selected_tab = st.tabs(tab_names)

    with selected_tab[0]:
        sales_ui()    # "국내/해외 판매 관리"

    with selected_tab[1]:   
        ltv_ui()    # "LTV 및 시장 예측 분석"

    with selected_tab[2]:
        economy_ui()      # "글로벌 경제 인사이트내"

    with selected_tab[3]:
        marketing_ui()    # "마케팅 캠페인 성과"


