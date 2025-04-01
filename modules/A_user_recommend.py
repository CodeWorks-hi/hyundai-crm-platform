# 고객 메인 대시보드  
    # 고객 맞춤 추천


import streamlit as st

def recommend_ui(df_employees, generate_html_table):
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

    # 예시 추천 (임시 하드코딩)
    st.markdown("### 🔍 추천 차량 예시")

    if 고객['관심차종'] == "SUV":
        st.success("✅ 추천 차량: 투싼, 싼타페, 코나")
    elif 고객['관심차종'] == "세단":
        st.success("✅ 추천 차량: 아반떼, 쏘나타, 그랜저")
    elif 고객['관심차종'] == "EV":
        st.success("✅ 추천 차량: 아이오닉 5, EV6, 코나 일렉트릭")
    else:
        st.success("✅ 추천 차량: 고객 맞춤형 추천은 곧 제공될 예정입니다.")

    st.markdown("---")

    st.markdown("#### 📊 향후 탑재될 AI 기반 추천 기능")
    st.markdown("""
    - 고객 설문 데이터 기반 차량 스펙/가격/연비/용도 최적화 분석
    - LTV 기반 추천 모델 (XGBoost 기반)
    - 지역 선호도 및 연령대별 구매 패턴 반영
    - 예산 범위 내 최적 구성 추천
    - 고객 행동 예측 기반 사전 제안 기능 포함 예정
    """)


