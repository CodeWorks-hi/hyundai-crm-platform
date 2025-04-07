# 판매·수출 관리
    # 판매·수출 관리 
        # 국내 판매 (차종/지역별 등)
            # 성장률 트렌드 분석


import streamlit as st

def domestic_growth_ui():
    st.subheader("판매·수출 관리")
    st.write("국내 판매 실적을 분석하는 페이지입니다.")
    st.write("차종/지역별 성장률 트렌드 분석")

    col1,col2,col3=st.columns(3)