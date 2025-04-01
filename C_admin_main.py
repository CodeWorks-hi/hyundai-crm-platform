import streamlit as st
import importlib

def app():
    st.title("본사 관리자 포털")

    tabs = st.tabs([
        "판매·수출 관리",
        "재고 및 공급망 관리",
        "생산·제조 현황",
        "탄소 배출량 모니터링",
        "사용자 및 환경 관리"
    ])

    tab_modules = [
        ("modules.C_admin_analytics", "analytics_ui"),
        ("modules.C_admin_inventory", "inventory_ui"),
        ("modules.C_admin_production", "production_ui"),
        ("modules.C_admin_eco", "eco_ui"),
        ("modules.C_admin_settings", "settings_ui"),
    ]

    for i, (module_path, function_name) in enumerate(tab_modules):
        with tabs[i]:
            try:
                module = importlib.import_module(module_path)
                getattr(module, function_name)()
            except Exception as e:
                st.error(f"모듈 로딩 오류: `{module_path}.{function_name}`\\n\n**{e}**")

    st.markdown("---")

    # ✔ 안전한 방식: 세션 상태로 페이지 전환
    if st.button("← 메인으로 돌아가기"):
        st.session_state.current_page = "home"
        st.rerun()
