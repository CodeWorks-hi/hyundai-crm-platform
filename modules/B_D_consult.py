import streamlit as st
import pandas as pd

def consult_ui():
    st.title("🧾 고객 상담 페이지")

    if "show_recommendation" not in st.session_state:
        st.session_state["show_recommendation"] = False
    if "고객정보" not in st.session_state or not isinstance(st.session_state["고객정보"], dict):
        st.session_state["고객정보"] = {"이름": "", "연락처": ""}
    else:
        st.session_state["고객정보"].setdefault("이름", "")
        st.session_state["고객정보"].setdefault("연락처", "")

    customer_df = pd.read_csv("data/customers.csv")
    customer_df["이름"] = customer_df["이름"].astype(str).str.strip()
    customer_df["연락처"] = customer_df["연락처"].astype(str).str.strip()

    consult_log_df = pd.read_csv("data/consult_log.csv")

    # 세로 3컬럼 상단: col1 - 고객 정보 / col2 - 추천 입력 / col3 - 추천 결과
    col1, col2, col3, col4, col5 = st.columns([0.8, 0.3, 1.5, 0.3, 2])

    with col1:
        default_name = st.session_state["고객정보"].get("이름", "")
        default_contact = st.session_state["고객정보"].get("연락처", "")
        selected_name = st.text_input("고객 성명", value=default_name)
        selected_contact = st.text_input("고객 연락처", value=default_contact)
        if selected_name and selected_contact:
            customer_info = customer_df.loc[(customer_df["이름"] == selected_name) & (customer_df["연락처"] == selected_contact), :]
            if not customer_info.empty:
                st.markdown(f"""
                <div style="background-color: #f4f4f4; border: 1px solid #ddd; padding: 12px; border-radius: 8px; margin-top: 10px;">
                    <div style="font-size: 16px; font-weight: 600; color: #333;">👤 {customer_info['이름'].values[0]}</div>
                    <div style="font-size: 14px; color: #555;">성별: {customer_info['성별'].values[0]}</div>
                    <div style="font-size: 14px; color: #555;">생년월일: {customer_info['생년월일'].values[0]}</div>
                    <div style="font-size: 14px; color: #555;">전화번호: {customer_info['연락처'].values[0]}</div>
                </div>
                """, unsafe_allow_html=True)
            else :
                st.error("❗ 설문조사 결과를 찾을 수 없습니다. 이름과 연락처를 확인해주세요.")

    with col3:
        st.warning("##### * 기본적으로 설문조사 결과 기반으로 채워놓고, 추가 입력할 항목 있으면 그것만 선택하게 할 예정.")
        matched_survey = customer_df[(customer_df["이름"] == selected_name) & (customer_df["연락처"] == selected_contact)]
        if matched_survey.empty:
            st.error("❗ 설문조사 결과를 찾을 수 없습니다. 이름과 연락처를 확인해주세요.")
            return
        survey_result = matched_survey.iloc[0]

        colA, colB = st.columns(2)
        with colA:
            st.selectbox("성별", [survey_result["성별"]], disabled=True)
            st.selectbox("예산 (만원)", [survey_result["예상예산_만원"]], disabled=True)
            st.selectbox("동승자 유형", [survey_result["동승인원구성"]], disabled=True)
            st.selectbox("최근 보유 차량", [survey_result["최근보유차종"]], disabled=True)
        with colB:
            st.selectbox("연령", [survey_result["연령대"]], disabled=True)
            st.selectbox("운전 용도", [survey_result["주요용도"]], disabled=True)
            st.selectbox("관심 차종", [survey_result["관심차종"]], disabled=True)
        if st.button("🚘 추천받기", use_container_width=True):
            st.session_state["show_recommendation"] = True

    with col5:
        st.warning("##### * 차량 추천 결과 박스입니다. 3종만 보여주고, 저장하기 버튼 있는 이유는 나중에 재고 관리 창에서 선택한 차종 먼저 보이게 하려고.")
        if st.session_state.get("show_recommendation", False):
            for i in range(1, 4):
                img_col, text_col, button_col = st.columns([1.5, 1.3, 1])
                with img_col:
                    st.write("")  # spacer
                    st.write("")  # spacer
                    st.markdown("## IMG")
                with text_col:
                    st.markdown(f"**🚗 추천 차량 {i}**")
                    st.write("• 연비: 12.5km/L")
                    st.write("• 가격: 4,200만 원~")
                with button_col:
                    with st.container():
                        st.write("")  # spacer
                        st.write("")  # spacer
                        if st.button(f"저장하기 {i}", key=f"save_{i}"):
                            st.session_state[f"saved_recommend_{i}"] = f"추천 차량 {i}"
                st.markdown("---")
        else:
            st.info("🚘 왼쪽에서 '추천받기' 버튼을 눌러 차량 추천을 확인하세요.")

    # 하단 두 컬럼
    st.divider()
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.warning("##### * 상담 요청 사항 및 설문 결과 파트입니다. 여기는 상담 요청 기록 consult_log.csv와 survey_result.csv 가져와서 표시합니다.")

        st.write("**상담 요청일:**", "2025-03-28")
        st.write("**상담 요청 내용:** 여행용 7인승 차량 추천 요청. 연비 중요.")

        st.write("**설문조사 결과 요약:**")
        st.markdown("""
        - ✅ 연령: 30대 초반
        - ✅ 운전 경험: 5년 이상
        - ✅ 주 이용 목적: 가족 여행, 레저
        - ✅ 희망 옵션: 넓은 트렁크, 연비, 안전장치
        """)

    with col_right:
        st.warning("##### * 상담 내용 기록창입니다. 아직 뭘 넣을지 확정은 아니고, 상담하면서 딜러가 내용 정리하면 좋겠다 싶어서 일단 넣어봤어요.")
        memo = st.text_area("상담 내용을 기록하세요", height=200)
        if st.button("📩 상담 결과 저장"):
            result = {
                "이름": customer_info["이름"],
                "전화번호": customer_info["전화번호"],
                "상담일": pd.Timestamp.now().strftime("%Y-%m-%d"),
                "상담내용": memo
            }
            result_df = pd.DataFrame([result])
            try:
                existing = pd.read_csv("data/consult_result.csv")
                result_df = pd.concat([existing, result_df], ignore_index=True)
            except FileNotFoundError:
                pass
            result_df.to_csv("data/consult_result.csv", index=False)
            st.success("상담 내용이 저장되었습니다.")