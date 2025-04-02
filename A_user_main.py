# 메인 페이지 (탭 메뉴 포함)   

import streamlit as st
import pandas as pd
import uuid
import datetime
import os
import importlib



# ▶️ 메인 앱
def app():
    st.title("고객 페이지")

    # 탭 메뉴 정의 (콤마 누락 수정됨)
    tabs = st.tabs([
         
        "차량 비교", 
        "casper",
        
        "대리점 및 정비소",
        "이벤트 및 공지사항",
        "고객센터"
    ])

    # 모듈명과 함수명 매핑
    tab_modules = [
        
        ("modules.A_user_comparison", "comparison_ui"),
        ("modules.A_user_casper", "casper_ui"),
        
        ("modules.A_user_dealer", "dealer_ui"),
        ("modules.A_user_event", "event_ui"),
        ("modules.A_user_support", "support_ui")
    ]

    

    st.markdown("---")
    if st.button("← 메인으로 돌아가기", key="bottom_back_button"):
        st.session_state.current_page = "home"
        st.rerun()

