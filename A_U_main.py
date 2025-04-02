import streamlit as st
import importlib
import pandas as pd

# ▶️ 메인 앱
def app():
    # 탭 이름과 연결 함수
    tabs = st.tabs([
        "차량 비교", "casper", "대리점 및 정비소", "이벤트 및 공지사항", "고객센터"
    ])

    tab_modules = [
        ("modules.A_U_comparison", "comparison_ui"),
        ("modules.A_U_casper", "casper_ui"),
        ("modules.A_U_dealer", "dealer_ui"),
        ("modules.A_U_event", "event_ui"),
        ("modules.A_U_support", "support_ui")
    ]
    
    for i, (module_path, function_name) in enumerate(tab_modules):
        with tabs[i]:
            try:
                module = importlib.import_module(module_path)
                getattr(module, function_name)()
            except Exception as e:
                st.markdown(f"**모듈 로딩 오류: `{module_path}.{function_name}`")
                st.error(str(e))

    st.markdown("---")

    # ✔ 안전한 방식: 세션 상태로 페이지 전환
    if st.button("← 메인으로 돌아가기"):
        st.session_state.current_page = "home"
        st.rerun()

        

