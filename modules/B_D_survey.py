import streamlit as st
import uuid
import datetime
import pandas as pd
import numpy as np
import os
import re

# ▶️ 경로 설정
CUSTOMER_CSV_PATH = "data/customers.csv"

def load_employees():
    if os.path.exists("data/employee.csv"):
        df = pd.read_csv("data/employee.csv")
        df["사번"] = df["사번"].astype(str).str.replace(",", "").str.strip()
        df["직원이름"] = df["직원이름"].astype(str).str.strip()
        return df
    else:
        return pd.DataFrame()


def load_customers():
    columns = [
        "고객ID", "상담자ID", "상담자명", "등록일", "이름", "연락처", "성별", "생년월일", "연령대",
        "거주지역", "관심차종", "방문목적", "월주행거리_km", "주요용도", "예상예산_만원", "선호색상",
        "동승인원구성", "중요요소1", "중요요소2", "중요요소3", "최근보유차종", "기타요청사항"
    ]
    if os.path.exists(CUSTOMER_CSV_PATH):
        return pd.read_csv(CUSTOMER_CSV_PATH)
    else:
        return pd.DataFrame(columns=columns)

def save_customer(info):
    df = load_customers()
    # 중복 연락처 체크
    if info[5] in df["연락처"].astype(str).tolist():
        st.warning("이미 등록된 연락처입니다.")
        return False
    df.loc[len(df)] = info
    df.to_csv(CUSTOMER_CSV_PATH, index=False)
    return True

def normalize_phone(phone):
    return re.sub(r"[^\d]", "", phone.strip())

def survey_ui(df_employees, generate_html_table):
    st.subheader("방문고객 설문조사")

    if "직원이름" not in st.session_state or st.session_state["직원이름"] == "":
        st.warning("상담자 정보를 먼저 등록하세요.")
        return

    with st.form("고객등록"):
        name, phon, birth, gender = st.columns([2,2,2,1])
        with name : 
            이름 = st.text_input("성명")
        with phon :
            연락처 = st.text_input("연락처")
        with birth :
            today = datetime.date.today()
            생년월일 = st.date_input(
                "생년월일",
                min_value=datetime.date(1950, 1, 1),
                max_value=today,
                value=datetime.date(1990, 1, 1))
        with gender :   
            is_male = st.toggle("남성 / 여성", value=True)
            성별 = "남성" if is_male else "여성"

        거주지역 = st.selectbox("거주 지역", [
            "서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시",
            "울산광역시", "세종특별자치시", "경기도", "강원도", "충청북도", "충청남도",
            "전라북도", "전라남도", "경상북도", "경상남도", "제주특별자치도"
        ])
        관심차종 = st.multiselect("관심 차종", ["캐스퍼", "캐스퍼 일렉트릭", "그랜저", "아반떼", "투싼", "기타"])
        방문목적 = st.selectbox("방문 목적", ["차량 상담", "구매 의사 있음", "시승 희망", "기타"])

        st.markdown("#### 추가 설문")
        월주행거리 = st.selectbox("월 주행거리(km)", ["500", "1000", "1500", "2000 이상"])
        주요용도 = st.multiselect("주요 운전 용도", ["출퇴근", "아이 통학", "주말여행", "레저활동", "업무차량"])
        예산 = st.selectbox("예상 예산 (만원)", ["1500", "2000", "2500", "3000", "3500 이상"])
        선호색상 = st.selectbox("선호 색상", ["흰색", "검정", "회색", "은색", "파랑", "빨강", "기타"])
        동승구성 = st.selectbox("동승 인원 구성", ["1인", "부부", "자녀1명", "자녀2명 이상", "부모님 동승"])
        중요1 = st.selectbox("가장 중요한 요소", ["연비", "가격", "디자인", "성능", "안전", "공간"])
        중요2 = st.selectbox("두번째로 중요한 요소", ["연비", "가격", "디자인", "성능", "안전", "공간"])
        중요3 = st.selectbox("세번째로 중요한 요소", ["연비", "가격", "디자인", "성능", "안전", "공간"])
        보유차종 = st.text_input("최근 보유 차량")
        기타 = st.text_area("기타 요청사항")

        if st.form_submit_button("설문조사 완료"):

            df_employees = load_employees()
            d_name = str(st.session_state["직원이름"]).strip()
            d_id = str(st.session_state["사번"]).replace(",", "").strip()

            today = datetime.date.today().isoformat()
            연령대 = f"{(datetime.date.today().year - 생년월일.year) // 10 * 10}대"

            matched = df_employees.loc[
                (df_employees["직원이름"] == d_name) &
                (df_employees["사번"] == d_id), :]

            if matched.empty:
                st.error("상담자 정보를 찾을 수 없습니다. 로그인 정보를 확인해 주세요.")
                return
            
            상담자ID = matched.iloc[0]["고유ID"]

            if 보유차종 is None:
                보유차종 = "-"
            if 기타 is None:
                기타 = "-"

            customer_info = [
                str(uuid.uuid4()), 상담자ID, st.session_state["직원이름"], today,
                이름, 연락처, 성별, 생년월일.isoformat(), 연령대,
                거주지역, ", ".join(관심차종), 방문목적,
                월주행거리, ", ".join(주요용도), 예산, 선호색상,
                동승구성, 중요1, 중요2, 중요3, 보유차종, 기타
            ]

            if save_customer(customer_info):
                st.session_state["고객정보"] = {
                    "이름": 이름,
                    "관심차종": ", ".join(관심차종),
                    "예상예산_만원": 예산,
                    "주요용도": ", ".join(주요용도)
                }
                st.success(f"{이름}님 설문조사가 완료되었습니다.")
