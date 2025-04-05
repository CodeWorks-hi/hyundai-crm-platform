# A_U_main.py
import streamlit as st
import pandas as pd
import importlib

# 페이지 전환 함수 (공통)
def switch_page(page):
    st.session_state.current_page = page
    st.rerun()

    # 공통 버튼 스타일 (위에 한 번만 선언)
    btn_style = """
        <style>
        div.stButton > button {
            padding: 10px 20px;
            font-size: 15px;
            border-radius: 8px;
            border: 1px solid #ccc;
            background-color: #f8f8f8;
            box-shadow: 1px 1px 4px rgba(0,0,0,0.1);
            transition: all 0.2s ease-in-out;
            cursor: pointer;
            display: block;
            margin: 0 auto;
        }
        </style>
    """

# 일반회원 홈화면 UI
def app():

    tabs = st.tabs([
        "홈화면", 
        "모델 확인", 
        "모델 비교", 
        "대리점 검색", 
        "상담 예약",
        "친환경 보조금", 
        "고객 센터", 
        "이벤트"
    ])

    tab_modules = [
        ("modules.A_U_home", "home_ui"),
        ("modules.A_U_comparison", "comparison_ui"),
        ("modules.A_U_detail", "detail_ui"),
        ("modules.A_U_map", "map_ui"),
        ("modules.A_U_consult", "consult_ui"),
        ("modules.A_U_eco", "eco_ui"),
        ("modules.A_U_support", "support_ui"),
        ("modules.A_U_event", "event_ui"),
    ]

    for i, (module_path, function_name) in enumerate(tab_modules):
        with tabs[i]:
            # try:
            module = importlib.import_module(module_path)
            getattr(module, function_name)()
            # except Exception as e:
            #     st.error(f"모듈 로딩 오류: `{module_path}.{function_name}`\n\n**{e}**")


        # ✔ 안전한 방식: 세션 상태로 페이지 전환
    if st.button("← 메인으로 돌아가기"):
        st.session_state.current_page = "home"
        st.rerun()





 