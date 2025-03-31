import streamlit as st
import pandas as pd
import uuid
import os

EMPLOYEE_CSV_PATH = "data/employee.csv"
EMPLOYEE_PHOTO_DIR = "data/employee_photos"

os.makedirs("data", exist_ok=True)
os.makedirs(EMPLOYEE_PHOTO_DIR, exist_ok=True)

def load_employees():
    if os.path.exists(EMPLOYEE_CSV_PATH):
        return pd.read_csv(EMPLOYEE_CSV_PATH)
    else:
        return pd.DataFrame(columns=["고유ID", "직원이름", "사진경로"])

def save_employees(df):
    df.to_csv(EMPLOYEE_CSV_PATH, index=False)

def app():
    st.title("본사 관리자 포털")

    tabs = st.tabs([
        "사용자 관리",
        "데이터 동기화 상태",
        "판매·수출 모니터링",
        "생산·제조 현황 분석",
        "재고 자동 경고",
        "수출입 국가별 분석",
        "설정 및 환경 관리"
    ])

    with tabs[0]:
        st.markdown("### 직원 등록")

        with st.form("employee_form", clear_on_submit=True):
            name = st.text_input("직원이름")
            photo = st.file_uploader("직원 사진", type=["jpg", "jpeg", "png"])
            submitted = st.form_submit_button("직원 등록")

            if submitted:
                if name and photo:
                    df = load_employees()
                    new_id = str(uuid.uuid4())

                    ext = os.path.splitext(photo.name)[1]
                    save_filename = f"{new_id}{ext}"
                    save_path = os.path.join(EMPLOYEE_PHOTO_DIR, save_filename)

                    with open(save_path, "wb") as f:
                        f.write(photo.getbuffer())

                    df.loc[len(df)] = [new_id, name, save_path]
                    save_employees(df)
                    st.success(f"{name} 님이 등록되었습니다.")
                else:
                    st.warning("이름과 사진을 모두 입력해주세요.")

        st.markdown("### 직원 목록")
        df_employees = load_employees()

        if df_employees.empty:
            st.info("등록된 직원이 없습니다.")
        else:
            for i, row in df_employees.iterrows():
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"**{row['직원이름']}**")
                    st.caption(f"ID: {row['고유ID']}")
                with col2:
                    if os.path.exists(row["사진경로"]):
                        st.image(row["사진경로"], width=100)
                    else:
                        st.warning("사진 없음")
                with col3:
                    if st.button("삭제", key=f"del_{row['고유ID']}"):
                        if os.path.exists(row["사진경로"]):
                            os.remove(row["사진경로"])
                        df_employees = df_employees[df_employees["고유ID"] != row["고유ID"]]
                        save_employees(df_employees)
                        st.success(f"{row['직원이름']} 님이 삭제되었습니다.")
                        st.experimental_rerun()

    with tabs[1]:
        st.write("🔄 데이터 동기화 상태 화면입니다.")

    with tabs[2]:
        st.write("📊 판매·수출 모니터링 화면입니다.")

    with tabs[3]:
        st.write("🏭 생산·제조 현황 분석 화면입니다.")

    with tabs[4]:
        st.write("⚠️ 재고 자동 경고 화면입니다.")

    with tabs[5]:
        st.write("🌐 수출입 국가별 분석 화면입니다.")

    with tabs[6]:
        st.subheader("⚙️ 시스템 설정")
        st.markdown("#### 🔧 환경 설정 항목")

    st.markdown("---")

    if st.button("← 메인으로 돌아가기"):
        st.switch_page("Home.py")
