import streamlit as st
import pandas as pd

def consult_ui():
    st.title("🧾 고객 상담 페이지")
    clicked = False

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
    col1, col2, col3, col4, col5 = st.columns([1.2, 0.1, 1.5, 0.1, 2])

    with col1:
        default_name = st.session_state["고객정보"].get("이름", "")
        default_contact = st.session_state["고객정보"].get("연락처", "")
        selected_name = st.text_input("고객 성명 입력", value=default_name)
        selected_contact = st.text_input("고객 연락처 입력", value=default_contact)    

        if selected_name and selected_contact :
            clicked = True
            st.markdown("---")
            customer_info = customer_df.loc[(customer_df["이름"] == selected_name) & (customer_df["연락처"] == selected_contact), :]
            if not customer_info.empty:
                st.markdown(f"""
                <div style="background-color: #e9f3fc; border: 2px solid #1570ef; padding: 18px 24px; border-radius: 10px; margin-top: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
                    <div style="font-size: 20px; font-weight: 700; color: #0f3c73; margin-bottom: 10px;">👤 고객 정보 요약</div>
                    <ul style="list-style-type: none; padding-left: 0; font-size: 15px; color: #1d2c3b;">
                        <li><strong>📛 이름:</strong> {customer_info['이름'].values[0]}</li>
                        <li><strong>📱 연락처:</strong> {customer_info['연락처'].values[0]}</li>
                        <li><strong>🎂 생년월일:</strong> {customer_info['생년월일'].values[0]}</li>
                        <li><strong>🚗 주요용도:</strong> {customer_info['주요용도'].values[0]}</li>
                        <li><strong>⭐ 관심차종:</strong> {customer_info['관심차종'].values[0]}</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else :
                st.error("❗ 회원 정보를 찾을 수 없습니다. 이름과 연락처를 확인해주세요.")

    with col3:
        matched_survey = customer_df[(customer_df["이름"] == selected_name) & (customer_df["연락처"] == selected_contact)]
        if matched_survey.empty:
            st.error("❗ 설문조사 결과를 찾을 수 없습니다. 이름과 연락처를 확인해주세요.")
            return
        survey_result = matched_survey.iloc[0]

        if clicked:
            colA, colB = st.columns(2)
            with colA:
                st.text_input("성별", value=survey_result["성별"], disabled=True)
                st.number_input("예산 (만원)", step=500, value=survey_result["예상예산_만원"])
                companies = [str(survey_result["동승인원구성"])] + ["1인", "부부", "자녀1명", "자녀2명 이상", "부모님 동승"]
                unique_companies = list(dict.fromkeys(companies))
                st.selectbox("동승자 유형", unique_companies)
                imp1 = [str(survey_result["중요요소1"])] + ["연비", "가격", "디자인", "성능", "안전", "공간"]
                unique_imp1 = list(dict.fromkeys(imp1))
                st.selectbox("가장 중요한 요소", unique_imp1)
                imp3 = [str(survey_result["중요요소3"])] + ["연비", "가격", "디자인", "성능", "안전", "공간"]
                unique_imp3 = list(dict.fromkeys(imp3))
                st.selectbox("세 번째로 중요한 요소", unique_imp3)
            with colB:
                st.text_input("연령", value=survey_result["연령대"], disabled=True)
                distances = [str(survey_result["월주행거리_km"])] + ["500", "1000", "1500", "2000 이상"]
                unique_distances = list(dict.fromkeys(distances))
                st.selectbox("예상 월간 주행 거리 (km)", unique_distances)
                colors = [str(survey_result["선호색상"])] + ["흰색", "검정", "회색", "은색", "파랑", "빨강", "기타"]
                unique_colors = list(dict.fromkeys(colors))
                st.selectbox("선호 색상", unique_colors)
                imp2 = [str(survey_result["중요요소2"])] + ["연비", "가격", "디자인", "성능", "안전", "공간"]
                unique_imp2 = list(dict.fromkeys(imp2))
                st.selectbox("두 번째로 중요한 요소", unique_imp2)
                st.text_input("최근 보유 차량", survey_result["최근보유차종"], disabled=True) # 이건 예측에 필요한가 애매
            st.multiselect("운전 용도", ["출퇴근", "아이 통학", "주말여행", "레저활동", "업무차량"])
            st.multiselect("관심 차종", ["캐스퍼", "캐스퍼 일렉트릭", "그랜저", "아반떼", "투싼", "기타"])
                
            if st.button("🚘 추천받기", use_container_width=True):
                st.session_state["show_recommendation"] = True

    with col5:
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
        matched_consult = consult_log_df.loc[
            (consult_log_df["이름"] == selected_name) &
            (consult_log_df["전화번호"] == selected_contact),
            :].sort_values(by="상담날짜", ascending=False).head(1)

        if not matched_consult.empty:
            latest = matched_consult.iloc[0]
            st.markdown("#### 🗂️ 최근 상담 요청 정보")
            st.markdown(f"""
            <div style="background-color: #fdfdfd; border: 1px solid #ccc; border-radius: 8px; padding: 15px; margin-top: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.05);">
                <p style="margin: 0 0 8px 0; font-size: 15px; color: #333;"><strong>📅 상담 요청일:</strong> {latest["상담날짜"]}</p>
                <p style="margin: 0 0 8px 0; font-size: 15px; color: #333;"><strong>⏰ 상담 시간:</strong> {latest["상담시간"]}</p>
                <p style="margin: 0; font-size: 15px; color: #333;"><strong>📝 상담 내용:</strong> {latest["상담내용"]}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("❕ 상담 요청 정보가 없습니다.")

        st.markdown("---")

        if not customer_info.empty:
            survey = customer_info.iloc[0]
            st.markdown("#### 📋 설문 조사 답변 내용")
            st.markdown(f"""
            <div style="background-color: #f6fbff; border: 1px solid #b3d4fc; border-radius: 8px; padding: 15px; margin-top: 8px;">
                <ul style="list-style-type: none; padding-left: 0; font-size: 14px; color: #1f2f40;">
                    <li><strong>🚘 주요 운전 용도:</strong> {survey['주요용도']}</li>
                    <li><strong>🎯 중요 요소:</strong> {survey['중요요소1']}, {survey['중요요소2']}, {survey['중요요소3']}</li>
                    <li><strong>🎨 선호 색상:</strong> {survey['선호색상']}</li>
                    <li><strong>🧍 동승 인원 구성:</strong> {survey['동승인원구성']}</li>
                    <li><strong>💰 예산 범위:</strong> {survey['예상예산_만원']} 만원</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("❕ 해당 회원 정보가 없습니다.")
        
        st.write("")

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