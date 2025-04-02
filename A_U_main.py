# A_U_main.py
import streamlit as st
import importlib
import pandas as pd
from modules.A_U_carousel import render_carousel
import base64
from dotenv import load_dotenv
from modules.A_U_kakao_auth import handle_kakao_callback, render_kakao_login_button
from modules.A_U_kakao_channel import render_kakao_buttons


def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 페이지 전환 함수 (공통)
def switch_page(page):
    st.session_state.current_page = page
    st.rerun()





def kakao_login_ui():
    st.title("🔐 카카오 로그인")
    handle_kakao_callback()
    render_kakao_login_button()


# 일반회원 홈화면 UI
def user_main_ui():
    
    

    # 차량 이미지 캐러셀 (Swiper.js 활용)
    car_data = [
        {"name": "IONIQ 9", "url": "https://www.hyundai.com/contents/mainbanner/main_kv_ioniq9-pc.png"},
        {"name": "Palisade", "url": "https://www.hyundai.com/contents/mainbanner/Main-KV_Car_PALISADE.png"},
        {"name": "Venue", "url": "https://www.hyundai.com/contents/mainbanner/Main-KV_Car_venue.png"},
        {"name": "Tucson", "url": "https://www.hyundai.com/contents/mainbanner/Main-KV_Car_TUCSON.png"},
        {"name": "Sonata", "url": "https://www.hyundai.com/contents/mainbanner/main_sonata_25my_w.png"},
        {"name": "Santa Fe", "url": "https://www.hyundai.com/contents/mainbanner/main-santafe-25my-kv-w.png"},
        {"name": "Casper Electric", "url": "https://www.hyundai.com/contents/mainbanner/Main-KV_Car_CASPER-Electric.png"},
    ]
    # 캐러셀 함수 ( 파라미터에 차 리스트 넣으면 실행 됨) 모듈 > A_U_carousel.py 만 수정
    render_carousel(car_data, height=400)

    col6, col1, col2, col3, col4, col5, col7, col8 = st.columns([2, 1, 1, 1, 1, 1, 1, 2])
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
    st.markdown(btn_style, unsafe_allow_html=True)

    with col6:
        st.header("")

    # 모델확인
    with col1:
        st.markdown(
            f"""
            <div style="text-align:center">
                <img src="data:image/png;base64,{get_base64_image('images/car.png')}" width="80" style="margin-bottom: 10px;"><br>
                <div style='font-weight: bold; font-size: 18px; margin-bottom: 10px;'>모델확인</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("이동", key="btn_car_compare"):
            switch_page("A_U_comparison")

    # 대리점 검색
    with col2:
        st.markdown(
            f"""
            <div style="text-align:center">
                <img src="data:image/png;base64,{get_base64_image('images/location.png')}" width="80" style="margin-bottom: 10px;"><br>
                <div style='font-weight: bold; font-size: 18px; margin-bottom: 10px;'>대리점 검색</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("이동", key="btn_map"):
            switch_page("A_U_map")

    # 상담 예약
    with col3:
        st.markdown(
            f"""
            <div style="text-align:center">
                <img src="data:image/png;base64,{get_base64_image('images/customer-service.png')}" width="80" style="margin-bottom: 10px;"><br>
                <div style='font-weight: bold; font-size: 18px; margin-bottom: 10px;'>상담 예약</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("이동", key="btn_consult"):
            switch_page("A_U_consult")
    # 시승 신청
    with col4:
        st.markdown(
            f"""
            <div style="text-align:center">
                <img src="data:image/png;base64,{get_base64_image('images/handle.png')}" width="80" style="margin-bottom: 10px;"><br>
                <div style='font-weight: bold; font-size: 18px; margin-bottom: 10px;'>시승신청</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("이동", key="btn_test_drive"):
            switch_page("A_U_test_drive")

    # 고객센터
    with col5: 
        st.markdown(
            f"""
            <div style="text-align:center">
                <img src="data:image/png;base64,{get_base64_image('images/location.png')}" width="80" style="margin-bottom: 10px;"><br>
                <div style='font-weight: bold; font-size: 18px; margin-bottom: 10px;'>고객 센터</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("이동", key="btn_support"):
            switch_page("A_U_support")

    with col7:  # 이벤트
        st.markdown(
            f"""
            <div style="text-align:center">
                <img src="data:image/png;base64,{get_base64_image('images/party.png')}" width="80" style="margin-bottom: 10px;"><br>
                <div style='font-weight: bold; font-size: 18px; margin-bottom: 10px;'>이벤트</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("이동", key="btn_event"):
            switch_page("A_U_event")
    with col8:
        pass
    

    st.markdown("---")
    colb, colc, cola= st.columns([1,4,1])
    with cola :
        render_kakao_buttons()
        kakao_login_ui()
    with colb:
        if st.button("← 메인으로 돌아가기"):
            switch_page("home")


# ▶️ 앱 진입점
def app():
    page = st.session_state.get("current_page", "user_main")

    if page == "user_main":
        user_main_ui()
    elif page == "A_U_comparison":   # 모델확인
        import modules.A_U_comparison as auto
        auto.comparison_ui()
    elif page == "A_U_map":   # 대리점 검색
        import modules.A_U_map as map
        map.map_ui()
    elif page == "A_U_consult":   # 삼담예약
        import modules.A_U_consult as consult
        consult.consult_ui()
    elif page == "A_U_event":   # 이벤트 
        import modules.A_U_event as event
        event.event_ui()
    elif page == "A_U_support":  # 고객센터
        import modules.A_U_support as support
        support.support_ui()
    elif page == "A_U_test_drive":  # 시승신청
        import modules.A_U_test_drive as test_drive
        test_drive.test_drive_ui()


 