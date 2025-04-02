import streamlit as st

def recommend_ui(df_employees):
    st.subheader("🚘 고객 맞춤 차량 추천")

    # 설문 데이터가 없을 경우 안내
    if "고객정보" not in st.session_state:
        st.warning("먼저 설문조사를 완료해주세요.")
        return

    # 고객 정보 불러오기
    고객 = st.session_state["고객정보"]

    # 기본 정보 출력
    st.markdown(f"**{고객['이름']}** 고객님을 위한 추천 결과입니다:")
    st.markdown(f"- 📌 관심 차종: **{고객['관심차종']}**")
    st.markdown(f"- 💰 예산: **{고객['예상예산_만원']}만원**")
    st.markdown(f"- 🎯 차량 용도: **{고객['주요용도']}**")

    st.markdown("---")
    st.info("👉 현재는 기본 정보만 제공되며, 추후 AI 기반 차량 추천 알고리즘이 탑재될 예정입니다.")
