import streamlit as st
import pandas as pd
from huggingface_hub import InferenceClient


TEXT_MODEL_ID = "google/gemma-2-9b-it"

def get_huggingface_token(model_type):
    tokens = {"gemma": st.secrets.get("HUGGINGFACE_API_TOKEN_GEMMA")}
    return tokens.get(model_type)

def generate_tag(request: str, model_name: str = TEXT_MODEL_ID) -> list:
    token = get_huggingface_token("gemma")
    if not token:
        st.error("Hugging Face API 토큰이 없습니다.")
        return []

    system_prompt = """
    [시스템 지시 사항]
    ### 상담 내용 분석
    - 입력된 글의 핵심 키워드 추출
    - 키워드 기반으로 태그 생성
    
    [입력 예시 및 태그 출력 예시]
    각 상담 내용에는 고객의 관심사/상황에 따라 다음과 같은 카테고리로 태그를 지정하세요:
    - 구매단계: 관심, 구매 가능성 있음, 구매 결정, 구매 미정
    - 방문여부: 첫방문, 재방문 예정, 재방문 완료
    - 관심사: 전기차 관심, SUV 관심, 혜택 관심, 시승 희망, 안전 우선, 연비 중시, 공간 우선
    - 기타: 1인용, 가족용, 부모님 동승, 예산 3000 이하, 상담 지속, 피드백 요청
    
    상담 내용: "재방문 의사 강함. 차량 구매는 아직 미정이나 혜택 관련해서 설명 더 드리면 구매하실 듯. 재방문 일자는 1주 내로 말씀해주시기로 함."
    태그: 재방문 예정, 구매 가능성 있음, 구매 미정, 혜택 관심, 상담 지속

    상담 내용: "차량 시승 완료, 다음 주 방문하시고 계약 예정, 차량 색상만 고민."
    태그: 구매 결정, 재방문 예정, 시승 완료, 색상 고민

    상담 내용: "아이 등하교용으로 안전한 SUV 필요, 트렁크 공간 중요, 시승 희망하시는 듯."
    태그: 관심, SUV 관심, 가족용, 아이 통학, 안전 우선, 공간 우선, 시승 희망

    상담 내용: "주말마다 캠핑을 다니시는 고객님. 짐이 많아서 공간이 중요함. 레저용으로 연비보단 공간이 우선."
    태그: 관심, 레저용, 공간 우선, 주말 여행, 짐 많음

    상담 내용: "출퇴근 용도의 저렴한 전기차 필요. 1인 운전 예정이심. 예산은 3000만원 이하라고 하심."
    태그: 전기차 관심, 출퇴근, 저예산, 1인용, 예산 3000 이하
    
    ----------------------------
    
    아래 상담 내용을 분석해 위와 같은 형식으로 쉼표로 구분된 태그들을 생성하세요.
    """

    full_prompt = f"{system_prompt}\n\n[상담 내용] : {request.strip()}"

    try:
        client = InferenceClient(model=model_name, token=token)
        response = client.text_generation(
            prompt=(f"""
                다음 상담 내용에 대한 태그들을 현대자동차 전문가 입장에서 쉼표로 구분된 한 줄의 문자열로 만들어줘.
                입력된 상담 내용을 바탕으로 핵심 키워드를 분석하고, 고객의 관심사나 요구 사항에 기반한 태그를 생성해.
                절대로 줄 바꿈 없이 출력해줘.\n\n{full_prompt}
            """),
            max_new_tokens=1000,
            temperature=0.3
        )
        st.write("📤 상담내용:", request)
        st.write("🔑 사용된 토큰:", token)
        st.write("📡 호출된 모델:", model_name)
        st.write("🧠 모델 응답 원문:", response)
 
        tag_line = response.strip().split("\n")[0]
        return [tag.strip() for tag in tag_line.split(",") if tag.strip()]
    except Exception as e:
        st.error(f"텍스트 생성 오류: {e}")
        return []


def consult_ui():
    st.title("🧾 고객 상담 페이지")
    clicked = False

    if "직원이름" not in st.session_state or st.session_state["직원이름"] == "":
        st.warning("딜러 정보를 먼저 등록하세요.")
        return
    
    if "show_recommendation" not in st.session_state:
        st.session_state["show_recommendation"] = False
    if "고객정보" not in st.session_state or not isinstance(st.session_state["고객정보"], dict):
        st.session_state["고객정보"] = {"상담자명": "", "연락처": ""}
    else:
        st.session_state["고객정보"].setdefault("상담자명", "")
        st.session_state["고객정보"].setdefault("연락처", "")

    customer_df = pd.read_csv("data/customers.csv")
    customer_df["상담자명"] = customer_df["상담자명"].astype(str).str.strip()
    customer_df["연락처"] = customer_df["연락처"].astype(str).str.strip()

    consult_log_df = pd.read_csv("data/consult_log.csv")

    # 세로 3컬럼 상단: col1 - 고객 정보 / col2 - 추천 입력 / col3 - 추천 결과
    col1, col2, col3, col4, col5 = st.columns([1.2, 0.1, 1.3, 0.1, 2])

    with col1:
        default_name = st.session_state["고객정보"].get("상담자명", "")
        default_contact = st.session_state["고객정보"].get("연락처", "")
        selected_name = st.text_input("고객 성명 입력", value=default_name)
        selected_contact = st.text_input("고객 연락처 입력", value=default_contact)    

        if selected_name and selected_contact :
            clicked = True
            st.markdown("---")
            customer_info = customer_df.loc[(customer_df["상담자명"] == selected_name) & (customer_df["연락처"] == selected_contact), :]
            if not customer_info.empty:
                st.markdown(f"""
                <div style="background-color: #e9f3fc; border: 2px solid #1570ef; padding: 18px 24px; border-radius: 10px; margin-top: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
                    <div style="font-size: 20px; font-weight: 700; color: #0f3c73; margin-bottom: 10px;">👤 고객 기초 정보</div>
                    <ul style="list-style-type: none; padding-left: 0; font-size: 15px; color: #1d2c3b;">
                        <li><strong>📛 이름:</strong> {customer_info['상담자명'].values[0]}</li>
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
                    <p style="margin: 0; font-size: 15px; color: #333;"><strong>📝 요청 사항:</strong> {latest["요청사항"]}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("❕ 상담 요청 정보가 없습니다.")

    with col3:
        matched_survey = customer_df[(customer_df["상담자명"] == selected_name) & (customer_df["연락처"] == selected_contact)]
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
                st.session_state["recom_budget"] = budget

                st.session_state["show_recommendation"] = True

                car_df = pd.read_csv("data/hyundae_car_list.csv")
                car_df = car_df.loc[car_df["브랜드"] != "기아", :]

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
                prior_list = list(set([prior1, prior2, prior3]))
                for i in prior_list :
                    if i == "연비" :
                        car_df = car_df.loc[car_df["연비"] >= car_df["연비"].mean(), :]
                    elif i == "가격" :
                        car_df = car_df.loc[car_df["기본가격"] <= budget * 11000, :]
                    elif i == "성능" :
                        car_df = car_df.loc[car_df["배기량"] >= car_df["배기량"].mean(), :]
                    elif i == "공간" :
                        if purp is not None :
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

                filtered_df = car_df.loc[car_df["기본가격"] >= car_df["기본가격"].mean(), :]

                if len(filtered_df) >= 3:
                    result_df = filtered_df.sample(3)
                elif len(filtered_df) > 0:
                    result_df = filtered_df.sample(len(filtered_df))
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

        # default_tags = generate_tag(memo, model_name=TEXT_MODEL_ID) if memo.strip() else []
        # st.write("📥 생성된 태그:", default_tags)
        default_tags = ["SUV", "가족용", "예산 3000 이하", "전기차 관심", "시승 희망", "재방문 예정"]
        selected_tags = st.multiselect("상담 태그 선택", default_tags, key="consult_tags")
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
        memo = st.text_area("상담 내용을 입력하세요", height=150, label_visibility="collapsed")

        if st.button("✅ 저장", use_container_width=True, key='save_memo'):
            cr_df = pd.read_csv("data/consult_log.csv")
            mask = (cr_df['이름'] == selected_name) & (cr_df['전화번호'] == selected_contact) & (cr_df["목적"] == "방문")
            
            if (cr_df.loc[mask, "완료여부"] == 0).any():
                if mask.any():
                    cr_df.loc[mask, "상담내용"] = memo.replace("\n", " ")
                    cr_df.loc[mask, "완료여부"] = 1
                    cr_df.loc[mask, "상담태그"] = ', '.join(selected_tags)
                    cr_df.to_csv("data/consult_log.csv", index=False)
                    st.success("✅ 상담 내용이 저장되었습니다.")
                else:
                    st.warning("해당 조건에 맞는 미완료 상담이 없습니다.")
            else:
                if (cr_df.loc[mask, "완료여부"] == 1).any():
                    st.warning("이미 상담이 완료된 상태입니다.")
                else:
                    # 새로운 상담 로그 행 추가
                    new_log = {
                        "상담자명": selected_name,
                        "전화번호": selected_contact,
                        "상담내용": memo,
                        "요청사항": "-",
                        "상담날짜": pd.Timestamp.now().strftime("%Y-%m-%d"),
                        "상담시간": pd.Timestamp.now().strftime("%H:%M"),
                        "상담태그": ', '.join(selected_tags),
                        "담당직원": st.session_state["직원이름"],
                        "답변내용": "-",
                        "고객피드백": "-",
                        "목적": "방문",
                        "완료여부": 1
                    }
                    cr_df = pd.concat([cr_df, pd.DataFrame([new_log])], ignore_index=True)
                    cr_df.to_csv("data/consult_log.csv", index=False)
                    st.success("✅ 상담 내용이 저장되었습니다.")

    st.markdown("###### ")

    with st.expander("🗂 원본 데이터 확인", expanded=False):
        tab1, tab2, tab3 = st.tabs(["고객 상담 신청 기록", "고객 설문조사 기록", "차량 상세 정보"])
        with tab1:
            base_df = pd.read_csv("data/consult_log.csv")
            st.dataframe(base_df, hide_index=True, use_container_width=True)
        with tab2:
            base_df = pd.read_csv("data/customers.csv")
            st.dataframe(base_df, hide_index=True, use_container_width=True)
        with tab3:
            base_df = pd.read_csv("data/hyundae_car_list.csv")
            st.dataframe(base_df, hide_index=True, use_container_width=True)