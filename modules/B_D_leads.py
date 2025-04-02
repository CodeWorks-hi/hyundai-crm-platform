import pandas as pd
import streamlit as st
import plotly.graph_objects as go

def leads_ui():
    st.markdown("### 👥 고객 리드 관리 대시보드")

    st.markdown("#### 김철수 고객님")

    st.warning("##### * 리드 등급 게이지. 고객의 충성도 및 구매의사, 이탈 가능성들 판단 가능한 탭")
    grade = 4  # 1~5 중 현재 고객 등급 (예시)

    st.markdown("**고객 리드 등급 (1~5)**")
    progress_percent = int(((grade - 1) / 4) * 100)
    st.progress(progress_percent)

    # 레이블 시각화
    st.markdown("""
<style>
.label-bar {
    display: flex;
    justify-content: space-between;
    margin-top: -0.5rem;
    font-size: 0.85rem;
    padding: 0 0.3rem;
    color: #555;
}
</style>
<div class="label-bar">
  <span>1단계</span>
  <span>2단계</span>
  <span>3단계</span>
  <span>4단계</span>
  <span>5단계</span>
</div>
""", unsafe_allow_html=True)
    
    st.markdown(f"현재 등급: {grade} / 5")

    # 컬럼 구성
    col1, col2, col3 = st.columns([1.2, 2, 0.1])

    with col1:
        st.warning("##### * 고객 등급 설명")
        st.info("등급 3 고객은 제품에 관심은 있으나 구매까지 추가 정보가 필요한 단계입니다.")

        st.warning("##### * 고객 서비스 이용 내역. 어떤 서비스를 얼마나 이용했는지.")
        st.success("✅ 차량 구매: 2회\n✅ B 서비스: 1회\n✅ C 서비스: 2회")

    with col2:
        colA, colB = st.columns(2)

        with colA:
            st.warning("##### * 고객 충성도 스코어링")
            # 예시 점수 데이터
            score_map = {"방문": 10, "상담신청": 30, "구매": 50}
            score = score_map["방문"] + score_map["상담신청"] + score_map["구매"]
            st.metric("누적 충성도 점수", f"{score}점")

        with colB:
            st.warning("##### * 어떤 거 넣으면 좋을지 모르겠는 페이지")

        st.markdown("##### * 📌 고객 맞춤 팔로업 제안")
        st.checkbox("✔ 다음 방문 시 추가 제품 소개")
        st.checkbox("✔ 구매 혜택 프로모션 안내")
        st.checkbox("✔ 장기 미응답 고객: 전화상담 권장")