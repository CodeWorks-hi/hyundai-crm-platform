# A_auto_mall.py

import streamlit as st
import pandas as pd
import uuid
import datetime
import os

df = pd.read_csv("data/casper_final.csv") # 캐스퍼 정보 불러오기

CUSTOMER_CSV_PATH = "data/customers.csv" # 고객정보
EMPLOYEE_CSV_PATH = "data/employee.csv" # 직원정보
os.makedirs("data", exist_ok=True)

# 고객 CSV 불러오기 또는 생성
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

# 고객 저장
def save_customer(info):
    df = load_customers()
    df.loc[len(df)] = info
    df.to_csv(CUSTOMER_CSV_PATH, index=False)




# 직원 데이터 로드 
@st.cache_data
def load_employees():
    if os.path.exists(EMPLOYEE_CSV_PATH):
        return pd.read_csv(EMPLOYEE_CSV_PATH)
    else:
        return pd.DataFrame(columns=["고유ID", "직원이름", "사진경로"])

df_employees = load_employees()

def generate_html_table(df: pd.DataFrame) -> str:
    html = """
    <style>
    .compare-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
        table-layout: fixed;
    }
    .compare-table th, .compare-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
        word-wrap: break-word;
    }
    .compare-table th {
        background-color: #f5f5f5;
        font-weight: bold;
    }
    .scroll-wrapper {
        max-height: 500px;
        overflow-y: auto;
        border: 1px solid #ccc;
        margin-top: 10px;
    }
    </style>
    <div class="scroll-wrapper">
    <table class="compare-table">
    """

    headers = ["항목"] + df["트림명"].tolist()
    html += "<tr>" + "".join(f"<th>{col}</th>" for col in headers) + "</tr>"

    transpose_df = df.set_index("트림명").T.reset_index()
    transpose_df.columns = ["항목"] + df["트림명"].tolist()

    for _, row in transpose_df.iterrows():
        html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"

    html += "</table></div>"
    return html


def app():
    st.title("설문조사 항목은 머신러닝 학습 및 추천 데이터로 구성, 딜러가 고객이 왔을때 차량 목록 보여주기, 고객정보입력하기, 차량 선택 해서 판매 할 경우 판매 등록, 상담내용등록, 고객 성향 파악 , 고객에게 맞춤 차량 추천 ")
    
    if st.button("← Home"):
        st.session_state.current_page = "home"
        st.rerun()
    tabs = st.tabs([
        "차량 추천", 
        "차량 비교", 
        "방문고객 설문조사", 
        "판매 등록",
        "AI 수요 예측",
        "고객 맞춤 추천",
        "casper"
    ])



    with tabs[0]:
        st.write("차량 추천 기능 예정. (대시보드 개요)")

    with tabs[1]:
        st.write("차량 비교 기능 예정. (판매 실적 현황)")

    with tabs[2]:
        st.subheader("설문조사")

        if "직원이름" not in st.session_state or st.session_state["직원이름"] == "":
            st.warning("상담자 정보를 먼저 등록하세요 (사이드바에서)")
        else:
            with st.form("고객등록"):
                이름 = st.text_input("이름")
                연락처 = st.text_input("연락처 (숫자만)", max_chars=11)
                성별 = st.radio("성별", ["남성", "여성"], horizontal=True)
                생년월일 = st.date_input("생년월일")
                거주지역 = st.selectbox("거주 지역", [
                    "서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시",
                    "울산광역시", "세종특별자치시", "경기도", "강원도", "충청북도", "충청남도",
                    "전라북도", "전라남도", "경상북도", "경상남도", "제주특별자치도"])
                관심차종 = st.multiselect("관심 차종", ["캐스퍼", "캐스퍼 일렉트릭", "그랜저", "아반떼", "투싼", "기타"])
                방문목적 = st.selectbox("방문 목적", ["차량 상담", "구매 의사 있음", "시승 희망", "기타"])

                st.markdown("---")
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

                submitted = st.form_submit_button("설문조사 완료")
                if submitted:
                    고객ID = str(uuid.uuid4())
                    today = datetime.date.today().isoformat()
                    연령대 = f"{(datetime.date.today().year - 생년월일.year) // 10 * 10}대"
                    상담자명 = st.session_state["직원이름"]
                    상담자ID = df_employees[df_employees["직원이름"] == 상담자명].iloc[0]["고유ID"]

                    customer_info = [
                        고객ID, 상담자ID, 상담자명, today, 이름, 연락처, 성별,
                        생년월일.isoformat(), 연령대, 거주지역, ", ".join(관심차종), 방문목적,
                        월주행거리, ", ".join(주요용도), 예산, 선호색상, 동승구성,
                        중요1, 중요2, 중요3, 보유차종, 기타
                    ]
                    save_customer(customer_info)

                    st.session_state["고객정보"] = {
                        "이름": 이름,
                        "관심차종": ", ".join(관심차종),
                        "예상예산_만원": 예산,
                        "주요용도": ", ".join(주요용도)
                    }

                    st.success(f"{이름}님 설문조사가 완료되었습니다.")


                    
    with tabs[3]:
        st.write("00 화면입니다. (생산 계획 관리)")

    with tabs[4]:
        st.write("00 화면입니다. (AI 수요 예측)")

    with tabs[5]:
        st.write("00 화면입니다. (고객 맞춤 추천)")

    with tabs[6]:
        # 데이터 불러오기
        df = pd.read_csv("data/casper_final.csv")

        # 캐스퍼 모델 분리
        casper = df[df["차종"].str.contains("캐스퍼", na=False) & ~df["차종"].str.contains("일렉트", na=False)]
        electric = df[df["차종"].str.contains("일렉트", na=False)]
        col2, col3 = st.columns([3,1])
            
        # 캐스퍼 카드 출력
        with col2:
            st.markdown("### 캐스퍼")

            for i in range(0, len(casper), 3):
                row = casper.iloc[i:i+3]
                cols = st.columns(3)
                for col, (_, item) in zip(cols, row.iterrows()):
                    with col:
                        st.image(item["img_url"], width=260)
                        st.markdown(f"**{item['차종']}**")
                        st.markdown(f"{item['트림명']}")
                        st.markdown(f"{item['기본가격(원)']:,}원")
                        
                        # 차량 선택 버튼
                        if st.button("이 차량 선택", key=f"선택_{item['트림명']}"):
                            st.session_state["선택차량"] = item.to_dict()
                            st.rerun()

            # 캐스퍼 비교 테이블
            with st.expander("캐스퍼 비교하기"):
                casper_compare = casper.drop(columns=["img_url"]).reset_index(drop=True)
                casper_html = generate_html_table(casper_compare.fillna(""))
                st.markdown(casper_html, unsafe_allow_html=True)

            # 캐스퍼 일렉트릭 모델
            st.markdown("### 캐스퍼 일렉트릭")

            for i in range(0, len(electric), 3):
                row = electric.iloc[i:i+3]
                cols = st.columns(3)
                for col, (_, item) in zip(cols, row.iterrows()):
                    with col:
                        st.image(item["img_url"], width=260)
                        st.markdown(f"**{item['차종']}**")
                        st.markdown(f"{item['트림명']}")
                        st.markdown(f"{item['기본가격(원)']:,}원")
                        
                        # 차량 선택 버튼
                        if st.button("이 차량 선택", key=f"선택_{item['트림명']}_elec"):
                            st.session_state["선택차량"] = item.to_dict()
                            st.rerun()

            # 일렉트릭 비교 테이블
            with st.expander("캐스퍼 일렉트릭 비교하기"):
                electric_compare = electric.drop(columns=["img_url"]).reset_index(drop=True)
                electric_html = generate_html_table(electric_compare.fillna(""))
                st.markdown(electric_html, unsafe_allow_html=True)

        with col3:
            st.markdown("### 차량 정보")

            if "선택차량" in st.session_state:
                car = st.session_state["선택차량"]
                st.image(car["img_url"], width=200)
                st.markdown(f"**{car['차종']} {car['트림명']}**")
                st.markdown(f"가격: {car['기본가격(원)']:,}원")

                if st.button("판매 등록으로 이동"):
                    st.session_state.current_page = "판매 등록"
                    st.rerun()

                st.markdown("---")
                st.markdown("**세부 정보**")
                for col in ['연료', '배기량(cc)', '최고출력(PS)', '공차중량(kg)', '전비_복합(km/kWh)', '주행거리_복합(km)']:
                    value = car.get(col)
                    if pd.notna(value):
                        st.markdown(f"- {col}: {value}")
            else:
                st.info("선택된 차량이 없습니다.")
            
        
        # 고객 입력 폼은 사이드바로 이동
        with st.sidebar:
            df_employees = load_employees()

            if "직원이름" not in st.session_state:
                st.session_state["직원이름"] = ""

            if st.session_state["직원이름"] == "":
                입력이름 = st.text_input("상담자 이름을 입력하세요")

                if st.button("메니져 로그인"):
                    matched = df_employees[df_employees["직원이름"] == 입력이름]
                    if not matched.empty:
                        st.session_state["직원이름"] = 입력이름
                        st.rerun()
                    else:
                        st.warning("등록된 직원이 아닙니다.")

            else:
                matched = df_employees[df_employees["직원이름"] == st.session_state["직원이름"]]

                if matched.empty:
                    st.warning("등록된 직원이 아닙니다.")
                    if st.button("로그아웃"):
                        st.session_state["직원이름"] = ""
                        st.rerun()
                else:
                    직원정보 = matched.iloc[0]

                    # 이미지 중앙 정렬을 위해 컬럼 사용
                    col_center = st.columns([1, 2, 1])[1]
                    with col_center:
                        st.image(직원정보["사진경로"], width=150)

                    # 텍스트 중앙 정렬
                    st.markdown(
                        f"<div style='text-align: center; font-size: 18px; margin-top: 5px;'><strong>{직원정보['직원이름']} 매니저</strong></div>",
                        unsafe_allow_html=True
                    )

                    if st.button("로그아웃"):
                        st.session_state["직원이름"] = ""
                        st.rerun()

            st.markdown("### 오늘의 고객님 ")

            # 고객 정보 출력
            if "고객정보" in st.session_state:
                고객 = st.session_state["고객정보"]
                st.markdown("### 오늘의 고객님")
                st.markdown(f"**이름**: {고객['이름']} 고객님")
                st.markdown(f"**관심 차종**: {고객['관심차종']}")
                st.markdown(f"**예산**: {고객['예상예산_만원']}만원")
                st.markdown(f"**용도**: {고객['주요용도']}")

    
