# 메인 페이지 (탭 메뉴 포함)   

import streamlit as st
import pandas as pd
import uuid
import datetime
import os
import importlib

# ▶️ 경로 설정
EMPLOYEE_CSV_PATH = "data/employee.csv"
os.makedirs("data", exist_ok=True)

# ▶️ 직원 데이터 로드
@st.cache_data
def load_employees():
    if os.path.exists(EMPLOYEE_CSV_PATH):
        df = pd.read_csv(EMPLOYEE_CSV_PATH)
        if "사진경로" not in df.columns:
            df["사진경로"] = ""
        if "인코딩" not in df.columns:
            df["인코딩"] = ""
        return df
    else:
        return pd.DataFrame(columns=["고유ID", "직원이름", "사번", "사진경로", "인코딩"])

df_employees = load_employees()

# ▶️ 테이블 HTML 생성
def generate_html_table(df: pd.DataFrame) -> str:
    html = """
    <style>
    .compare-table { width: 100%; border-collapse: collapse; font-size: 14px; table-layout: fixed; }
    .compare-table th, .compare-table td { border: 1px solid #ddd; padding: 8px; text-align: center; word-wrap: break-word; }
    .compare-table th { background-color: #f5f5f5; font-weight: bold; }
    .scroll-wrapper { max-height: 500px; overflow-y: auto; border: 1px solid #ccc; margin-top: 10px; }
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


# ▶️ 메인 앱

def app():
    st.title("고객 페이지")

    # 상단 버튼에 고유 키 추가
    if st.button("← 메인으로 돌아가기", key="top_back_button"):
        st.session_state.current_page = "home"
        st.rerun()

    tabs = st.tabs([
        "차량 추천", 
        "차량 비교", 
        "방문고객 설문조사", 
        "고객 맞춤 추천",
        "casper"
    ])

    # ▶️ 탭별 연결할 모듈과 함수 정의
    tab_modules = [
        (None, None),                                                                       # 차량 추천은 구현 예정
        ("modules.A_user_comparison", "comparison_ui"),                                     # 차량 비교
        ("modules.A_user_survey", "survey_ui"),                                             # 방문고객 설문조사
        ("modules.A_user_personalized_recommend", "personalized_recommend_ui"),             # 고객 맞춤 추천
        ("modules.A_user_casper", "casper_ui")                                              # 캐스퍼 비교 및 선택
    ]


    for i, (module_path, function_name) in enumerate(tab_modules):
        with tabs[i]:
            if module_path is None:
                st.write("기능 준비 중입니다.")
            else:
                try:
                    module = importlib.import_module(module_path)
                    getattr(module, function_name)(df_employees, generate_html_table)
                except Exception as e:
                    st.error(f"모듈 로딩 오류: `{module_path}.{function_name}`\n\n**{e}**")
                    
    st.markdown("---")

    if st.button("← 메인으로 돌아가기", key="bottom_back_button"):
        st.session_state.current_page = "home"
        st.rerun()



    # ▶️ 사이드바 고객 입력 및 로그인 폼
    with st.sidebar:
        df_employees = load_employees()

        if "직원이름" not in st.session_state:
            st.session_state["직원이름"] = ""
        if "사번" not in st.session_state:
            st.session_state["사번"] = ""

        if st.session_state["직원이름"] == "":
            입력이름 = st.text_input("직원이름", value="홍길동")
            입력사번 = st.text_input("사번", value="202504010524")

            if st.button("매니저 로그인", key="manager_login_button"):
                입력이름 = 입력이름.strip()
                입력사번 = 입력사번.strip()
                df_employees["직원이름"] = df_employees["직원이름"].astype(str).str.strip()
                df_employees["사번"] = df_employees["사번"].astype(str).str.strip()

                matched = df_employees[
                    (df_employees["직원이름"] == 입력이름) &
                    (df_employees["사번"] == 입력사번)
                ]

                if not matched.empty:
                    st.session_state["직원이름"] = 입력이름
                    st.session_state["사번"] = 입력사번
                    st.rerun()
                else:
                    st.warning("❌ 이름 또는 사번이 올바르지 않습니다.")

        else:
            df_employees["직원이름"] = df_employees["직원이름"].astype(str).str.strip()
            df_employees["사번"] = df_employees["사번"].astype(str).str.strip()

            matched = df_employees[
                (df_employees["직원이름"] == st.session_state["직원이름"]) &
                (df_employees["사번"] == st.session_state["사번"])
            ]

            if not matched.empty:
                직원정보 = matched.iloc[0]
                col_center = st.columns([1, 2, 1])[1]
                with col_center:
                    if 직원정보["사진경로"] and os.path.exists(직원정보["사진경로"]):
                        st.image(직원정보["사진경로"], width=150)
                    else:
                        st.info("사진이 없습니다.")

                st.markdown(
                    f"<div style='text-align: center; font-size: 18px; margin-top: 5px;'><strong>{직원정보['직원이름']} 매니저</strong><br>사번: {직원정보['사번']}</div>",
                    unsafe_allow_html=True
                )

                if st.button("로그아웃", key="logout_button"):
                    st.session_state["직원이름"] = ""
                    st.session_state["사번"] = ""
                    st.rerun()
            else:
                st.error("⚠️ 등록된 직원 정보와 일치하지 않습니다. 로그아웃 후 다시 시도해주세요.")
                if st.button("로그아웃", key="error_logout_button"):
                    st.session_state["직원이름"] = ""
                    st.session_state["사번"] = ""
                    st.rerun()

        st.markdown("### 로그인 해주세요 ")

