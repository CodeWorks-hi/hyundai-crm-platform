# 고객 메인 대시보드  
    # 고객 맞춤 추천


import streamlit as st

def recommend_ui(df_employees, generate_html_table): 
    st.subheader("고객 맞춤 차량 추천")

    if "고객정보" not in st.session_state:
        st.warning("먼저 설문조사를 완료해주세요.")
        return

    고객 = st.session_state["고객정보"]
    st.markdown(f"**{고객['이름']}** 고객님을 위한 추천 결과:")
    st.markdown(f"- 관심 차종: {고객['관심차종']}")
    st.markdown(f"- 예산: {고객['예상예산_만원']}만원")
    st.markdown(f"- 용도: {고객['주요용도']}")
    st.info("👉 추후 AI 기반 추천 로직이 탑재됩니다.")


