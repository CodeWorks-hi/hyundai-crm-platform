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
    col1, col2, col3, col4, col5 = st.columns([1.2, 0.1, 1.3, 0.1, 2])

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
                    <div style="font-size: 20px; font-weight: 700; color: #0f3c73; margin-bottom: 10px;">👤 고객 기초 정보</div>
                    <ul style="list-style-type: none; padding-left: 0; font-size: 15px; color: #1d2c3b;">
                        <li><strong>📛 이름:</strong> {customer_info['이름'].values[0]}</li>
                        <li><strong>📱 연락처:</strong> {customer_info['연락처'].values[0]}</li>
                        <li><strong>🎂 생년월일:</strong> {customer_info['생년월일'].values[0]}</li>
                        <li><strong>🗺️ 거주지역:</strong> {customer_info['거주지역'].values[0]}</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else :
                st.error("❗ 회원 정보를 찾을 수 없습니다. 이름과 연락처를 확인해주세요.")

            st.write("")

            matched_consult = consult_log_df.loc[
                (consult_log_df["이름"] == selected_name) &
                (consult_log_df["전화번호"] == selected_contact),
                :].sort_values(by="상담날짜", ascending=False).head(1)

            if not matched_consult.empty:
                latest = matched_consult.iloc[0]
                st.markdown(f"""
                <div style="background-color: #fdfdfd; border: 1px solid #ccc; border-radius: 8px; padding: 15px; margin-top: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.05);">
                    <div style="font-size: 20px; font-weight: 700; color: #0f3c73; margin-bottom: 10px;">🗂️ 최근 상담 요청 정보</div>
                    <p style="margin: 0 0 8px 0; font-size: 15px; color: #333;"><strong>📅 상담 요청일:</strong> {latest["상담날짜"]}</p>
                    <p style="margin: 0 0 8px 0; font-size: 15px; color: #333;"><strong>⏰ 상담 시간:</strong> {latest["상담시간"]}</p>
                    <p style="margin: 0; font-size: 15px; color: #333;"><strong>📝 상담 내용:</strong> {latest["요청사항"]}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("❕ 상담 요청 정보가 없습니다.")

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
                budget_raw = survey_result["예상예산_만원"]
                if isinstance(budget_raw, str) and "3500" in budget_raw:
                    budg = 3500
                else:
                    try:
                        budg = int(budget_raw)
                    except:
                        budg = 0
                budget = st.number_input("예산 (만원)", step=500, min_value=0, value=budg)
                companies = [str(survey_result["동승인원구성"])] + ["1인", "부부", "자녀1명", "자녀2명 이상", "부모님 동승"]
                unique_companies = list(dict.fromkeys(companies))
                company = st.selectbox("동승자 유형", unique_companies)
            with colB:
                st.text_input("연령대", value=survey_result["연령대"], disabled=True)
                if survey_result["월주행거리_km"] == "2000 이상" :
                    distance = 2000
                else :
                    distance = int(survey_result["월주행거리_km"])
                st.number_input("예상 월간 주행 거리 (km)", step=500, min_value=0, value=distance)
                colors = [str(survey_result["선호색상"])] + ["흰색", "검정", "회색", "은색", "파랑", "빨강", "기타"]
                unique_colors = list(dict.fromkeys(colors))
                st.selectbox("선호 색상", unique_colors)

            purp = st.multiselect("운전 용도", ["출퇴근", "아이 통학", "주말여행", "레저활동", "업무차량"])

            colC, colD = st.columns(2)
            with colC:
                imp1 = [str(survey_result["중요요소1"])] + ["연비", "가격", "디자인", "성능", "안전", "공간"]
                unique_imp1 = list(dict.fromkeys(imp1))
                prior1 = st.selectbox("가장 중요한 요소", unique_imp1)
                imp3 = [str(survey_result["중요요소3"])] + ["연비", "가격", "디자인", "성능", "안전", "공간"]
                unique_imp3 = list(dict.fromkeys(imp3))
                prior3 = st.selectbox("세 번째로 중요한 요소", unique_imp3)
            with colD:
                imp2 = [str(survey_result["중요요소2"])] + ["연비", "가격", "디자인", "성능", "안전", "공간"]
                unique_imp2 = list(dict.fromkeys(imp2))
                prior2 = st.selectbox("두 번째로 중요한 요소", unique_imp2)
                st.text_input("최근 보유 차량", survey_result["최근보유차종"], disabled=True)
                
            if st.button("🚘 추천받기", use_container_width=True):
                st.session_state["show_recommendation"] = True

                car_df = pd.read_csv("data/hyundae_car_list.csv")

                # 예산에 따라 추천 차량 필터링
                car_df = car_df.loc[car_df["기본가격"] <= budget * 15000, :]

                # 동승 유형에 따라 추천 차량 필터링
                def company_type(company):
                    return {
                        "1인": "소형",
                        "부부": "준중형",
                        "자녀1명": "준중형",
                        "자녀2명 이상": "중형",
                        "부모님 동승": "중형"
                    }.get(company, "")

                comp_car = company_type(company)
                car_df = car_df.loc[car_df["차량구분"] == comp_car, :]

                # 우선 순위별 필터링
                prior_list = list(set[prior1, prior2, prior3])
                for i in prior_list :
                    if i == "연비" :
                        car_df = car_df.loc[car_df["연비"] >= car_df["연비"].mean(), :]
                    elif i == "가격" :
                        car_df = car_df.loc[car_df["기본가격"] <= budget * 13000, :]
                    elif i == "성능" :
                        car_df = car_df.loc[car_df["배기량"] >= car_df["배기량"].mean(), :]
                    elif i == "공간" :
                        if j is not None :
                            for j in purp :
                                if j == "출퇴근":
                                    car_df = car_df.loc[(car_df["연비"] >= car_df["연비"].mean()) & (car_df["차량구분"].isin(["소형", "준중형", "중형"])), :]
                                elif j == "아이 통학":
                                    car_df = car_df.loc[car_df["차량구분"].isin(["준중형", "중형"]), :]
                                elif j == "주말여행":
                                    car_df = car_df.loc[car_df["차량구분"].isin(["중형", "대형"]) & (car_df["차량형태"].isin(["SUV", "승합차"])), :]
                                elif j == "레저활동":
                                    car_df = car_df.loc[car_df["차량구분"].isin(["중형", "대형"]) & (car_df["차량형태"] == "SUV"), :]
                                elif j == "업무차량":
                                    car_df = car_df.loc[car_df["차량구분"].isin(["대형"]) & (car_df["차량형태"] == "승합차"), :]

                if len(car_df) >= 3:
                    # result_df = car_df.sample(3)
                    result_df = car_df.loc[car_df["기본가격"] >= car_df["기본가격"].mean(), :].sample(3)
                elif len(car_df) > 0:
                    # result_df = car_df.sample(len(car_df))  # 가능한 만큼만 추천
                    result_df = car_df.loc[car_df["기본가격"] >= car_df["기본가격"].mean(), :].sample(len(car_df))
                else:
                    st.warning("추천 조건을 만족하는 차량이 없습니다.")
                    return
                
                st.session_state["추천결과"] = result_df.reset_index(drop=True)


    with col5:
        if "추천결과" in st.session_state:
            display_df = st.session_state["추천결과"]
            for i in range(len(display_df)):
                row = display_df.iloc[i]
                img_col, col_lm, text_col, col_rm, button_col = st.columns([1.4, 0.1, 1.5, 0.1, 1])
                with img_col:
                    st.header("")
                    st.image(image=row["img_url"])  # 실제 이미지 경로 삽입 가능
                with text_col:
                    st.markdown(f"##### **추천 차량 {i+1}**")
                    st.markdown(f"###### **{row['모델명']} ({row['트림명']})**")
                    st.write(f"• 연료 유형: {row['연료구분']}")
                    if row['연료구분'] == '전기' :
                        st.write(f"• 연비: {row['연비']} km/kWh")
                    else :
                        st.write(f"• 연비: {row['연비']} km/L")
                    st.write(f"• 가격: {row['기본가격']:,} 원~")
                with button_col:
                    with st.container():
                        st.header("")
                        if st.button(f"저장 {i+1}", key=f"save_{i+1}"):
                            st.session_state[f"saved_recommend_{i+1}"] = row['모델명']
                            st.session_state[f"saved_recommend_trim_{i+1}"] = row['트림명']
                st.markdown("---")
        else:
            st.info("🚘 왼쪽에서 '추천받기' 버튼을 눌러 차량 추천을 확인하세요.")

    # 하단 두 컬럼
    st.divider()
    col_left, col_midleft, col_mid, col_midright, col_right = st.columns([1, 0.1, 1, 0.1, 1])

    with col_left:
        if not customer_info.empty:
            survey = customer_info.iloc[0]
            st.markdown("#### 📋 설문 조사 답변 내용")
            st.markdown(f"""
            <div style="background-color: #f6fbff; border: 1px solid #b3d4fc; border-radius: 8px; padding: 15px; margin-top: 8px;">
                <ul style="list-style-type: none; padding-left: 0; font-size: 14px; color: #1f2f40;">
                    <li><strong>💰 예산 범위:</strong> {budg} 만원</li>
                    <li><strong>🚘 주요 운전 용도:</strong> {survey['주요용도']}</li>
                    <li><strong>🎯 중요 요소:</strong> {survey['중요요소1']}, {survey['중요요소2']}, {survey['중요요소3']}</li>
                    <li><strong>🎨 선호 색상:</strong> {survey['선호색상']}</li>
                    <li><strong>🧍 동승자 유형:</strong> {survey['동승인원구성']}</li>
                    <li><strong>🔘 기타 요청 사항:</strong> {survey['기타요청사항']}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("❕ 해당 회원 정보가 없습니다.")
        
        st.write("")

    with col_right:
        st.markdown("#### 🏷️ 상담 태그 분류")
        st.markdown(
            "<div style='font-size: 14px; color: #666; margin-bottom: 6px;'>상담 내용을 분류하기 위한 태그를 선택하거나 직접 입력하세요.</div>",
            unsafe_allow_html=True
        )
        default_tags = ["SUV", "가족용", "예산 3000 이하", "전기차 관심", "시승 희망", "재방문 예정"]
        selected_tags = st.multiselect("상담 태그 선택", default_tags)
        custom_tag = st.text_input("기타 태그 직접 입력")
        if custom_tag and custom_tag not in selected_tags:
            selected_tags.append(custom_tag)
        if len(selected_tags) == 0:
            selected_tags = "-"

        st.markdown("##### ✅ 선택된 태그")
        st.markdown(
            f"<div style='background-color: #f2f7fb; padding: 10px; border-radius: 8px; min-height: 40px; font-size: 13.5px; color: #1d3557;'>{', '.join(selected_tags) if selected_tags else '선택된 태그 없음'}</div>",
            unsafe_allow_html=True
        )

    with col_mid:
        st.markdown("#### 📝 상담 내용 메모")
        st.markdown(
            "<div style='font-size: 14px; color: #666; margin-bottom: 6px;'>고객과 나눈 상담 주요 내용을 기록해 주세요.</div>",
            unsafe_allow_html=True,
        )
        memo = st.text_area("상담 내용을 입력하세요", height=200, label_visibility="collapsed")
        
        if st.button("✅ 저장", use_container_width=True, key='save_memo'):
            cr_df = pd.read_csv("data/consult_log.csv")
            mask = (cr_df['이름'] == selected_name) & (cr_df['전화번호'] == selected_contact) & (cr_df["완료여부"] == 0)
            
            if mask.any():
                cr_df.loc[mask, "상담내용"] = memo
                cr_df.loc[mask, "완료여부"] = 1
                cr_df.loc[mask, "상담태그"] = ', '.join(selected_tags)
                cr_df.to_csv("data/consult_log.csv", index=False)
                st.success("✅ 상담 내용이 저장되었습니다.")
            else:
                st.warning("해당 조건에 맞는 미완료 상담이 없습니다.")