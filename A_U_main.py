# A_U_main.py
import streamlit as st
import importlib
import pandas as pd
from streamlit_carousel import carousel

# 🔁 페이지 전환 함수 (공통)
def switch_page(page):
    st.session_state.current_page = page
    st.rerun()

# ✅ 일반회원 홈화면 UI
def user_main_ui():
    st.title("일반회원 전용 서비스")

    image_urls = [
        "https://www.hyundai.com/contents/mainbanner/main_kv_ioniq9-pc.png",
        "https://www.hyundai.com/contents/mainbanner/Main-KV_Car_PALISADE.png",
        "https://www.hyundai.com/contents/mainbanner/Main-KV_Car_venue.png",
        "https://www.hyundai.com/contents/mainbanner/Main-KV_Car_TUCSON.png",
        "https://www.hyundai.com/contents/mainbanner/main_sonata_25my_w.png",
        "https://www.hyundai.com/contents/mainbanner/main-santafe-25my-kv-w.png",
        "https://www.hyundai.com/contents/mainbanner/Main-KV_Car_CASPER-Electric.png"
    ]

    carousel(items=[{"img": url, "title": "", "text": ""} for url in image_urls])
    st.divider()

    col6, col1, col2, col3, col4, col5, col7 = st.columns([1, 1, 1, 1, 1, 1, 1])

    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/743/743007.png", width=60)
        st.markdown("#### 모델확인")
        if st.button("이동", key="btn_car_compare"):
            switch_page("A_U_comparison")

    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/1042/1042339.png", width=60)
        st.markdown("#### 친환경차량")
        if st.button("이동", key="btn_event"):
            switch_page("A_U_event")

    with col3:
        st.image("https://cdn-icons-png.flaticon.com/512/535/535137.png", width=60)
        st.markdown("#### 매장찾기")
        if st.button("이동", key="btn_support"):
            switch_page("A_U_support")

    st.markdown("---")
    if st.button("← 메인으로 돌아가기"):
        switch_page("home")


# ▶️ 앱 진입점
def app():
    page = st.session_state.get("current_page", "user_main")

    if page == "user_main":
        user_main_ui()
    elif page == "A_U_comparison":
        import modules.A_U_comparison as auto
        auto.comparison_ui()
    elif page == "A_U_event":
        import modules.A_U_event as dealer
        dealer.event_ui()
    elif page == "A_U_support":
        import modules.A_U_support as admin
        admin.support_ui()
    elif page == "A_U_detail":
        import modules.A_U_detail as detail
        detail.detail_ui()