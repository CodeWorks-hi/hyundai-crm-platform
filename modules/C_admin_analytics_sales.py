# 판매·수출 관리
    # 판매 관리 (차종/지역별 등),수출입 국가별 분석



import streamlit as st

def analytics_sales_ui():
    st.title("수출입 국가별 분석")

    st.write("국가별 수출입 데이터를 분석하고 시각화하는 페이지입니다.")

    if st.button("← 관리자 포털로 돌아가기"):
        st.switch_page("C_admin_main.py")
