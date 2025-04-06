# 예: B_dealer_hub.py
import importlib
import streamlit as st
import os
import pandas as pd
import base64

# ▶️ 이미지 base64 인코딩 함수
def get_base64_image(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ▶️ 로고 + 타이틀 레이아웃
def render_logo_title():
    logo_base64 = get_base64_image("images/hyundae_kia_logo.png")

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
            <img src="data:image/png;base64,{logo_base64}" alt="로고" width="60" style="width: 120px; height: auto; border-radius: 8px;">
            <h1 style="margin: 0; font-size: 28px;">현대기아 모터스 전용 관리페이지</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

# ▶️ 호출
render_logo_title()

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

# ▶️ 테이블 HTML 생성 함수
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


def app():
    tabs = st.tabs([
        "대시보드",     # Overview 대체 – 직관적이고 고급스러움
        "고객 설문",   # Surveys – 응답보다 더 부드러운 표현
        "상담 이력",     # Consults – 상담 + 기록 의미
        "AI 추천",
        "재고 현황",     # Inventory – 관리보다 직관적
        "판매 등록",     # Orders – 그대로 유지 가능
        "리드 추적",     # Leads – 동적 느낌
        "데이터 뷰",      # Data Lab – 원본 확인보다 더 모던함
        # "상담AI테스트"      # 테스트
    ])

    tab_modules = [
        ("modules.B_D_dashboard", "dashboard_ui"),
        ("modules.B_D_survey", "survey_ui"),
        ("modules.B_D_consult", "consult_ui"),                     # 고객 상담 정보, 차량 추천
        ("modules.B_D_demand_forecast", "demand_forecast_ui"),          # AI 수요 예측
        ("modules.B_D_inventory", "inventory_ui"),                     # 재고 현황, 발주 추천, 마진 분석
        ("modules.B_D_sales_registration", "sales_registration_ui"),         # 판매 등록
        ("modules.B_D_leads", "leads_ui"),                             # 리드 퍼널, 스코어링, 자동 팔로업
        ("modules.B_D_data", "data_preview_ui"),      # 데이터 미리보기
    ]

# 각 탭에 대응하는 함수 실행
    for i, (module_path, function_name) in enumerate(tab_modules):
        with tabs[i]:
            try:
                module = importlib.import_module(module_path)
                func = getattr(module, function_name)

                # 함수 인자 조건 분기
                if function_name in ["survey_ui", "comparison_ui", "casper_ui"]:
                    func(df_employees, generate_html_table)
                elif function_name == "recommend_ui":
                    func(df_employees)
                else:
                    func()  # 인자가 없는 함수 (이벤트/공지, 딜러 찾기 등)

            except Exception as e:
                st.error(f"❌ `{module_path}.{function_name}` 로딩 중 오류:\n\n{e}")

    # ▶️ 사이드바 - 직원 로그인 UI
    with st.sidebar:
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
                st.error("⚠️ 등록된 직원 정보와 일치하지 않습니다.")
                if st.button("로그아웃", key="error_logout_button"):
                    st.session_state["직원이름"] = ""
                    st.session_state["사번"] = ""
                    st.rerun()
        st.markdown("### 로그인 해주세요 ")



    st.markdown("---")
    col11, col12, col13 =  st.columns([1, 6, 1])
    # ✔ 안전한 방식: 세션 상태로 페이지 전환
    with col13:
        pass
    with col11:
        if st.button("← 메인으로 돌아가기"):
            st.session_state.current_page = "home"
            st.rerun()
    with col12:
        st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.9rem; margin-top: 30px;'>
        © 2025 Hyundai & Kia Export Dashboard. All rights reserved.
        </div>
        """,
        unsafe_allow_html=True
        )
