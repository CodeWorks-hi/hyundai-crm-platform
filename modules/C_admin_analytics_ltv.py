# 판매·수출 관리
    # LTV 모델 결과, 시장 트렌드, 예측 분석



import streamlit as st


def analytics_ltv_ui():
    st.write("LTV 모델 결과, 시장 트렌드, 예측 분석 페이지입니다.")
    st.write("LTV 모델 결과를 분석하고 시장 트렌드를 예측하는 페이지입니다.") 

    if st.button("← 관리자 포털로 돌아가기"):
        st.switch_page("C_admin_main.py")
