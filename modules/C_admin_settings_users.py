# 사용자 관리
# 직원 등록, 삭제, 수정, 조회
# 직원 등록시 사진도 함께 등록
# 직원 등록시 사진은 저장되고, 사진 경로만 DB에 저장
# 직원 등록시 사진은 /data/employee_photos/ 디렉토리에 저장
# 직원 등록시 고유ID는 uuid.uuid4()로 생성
# 직원 목록은 /data/employee.csv 파일에 저장
# 직원 목록은 pandas DataFrame으로 관리
# 직원 목록은 고유ID, 직원이름, 사진경로로 구성
# 직원 목록은 등록된 직원이 없을 경우에 대한 예외 처리
# 데이터 동기화 상태



import os
import streamlit as st
import pandas as pd
import uuid

# 경로 설정
EMPLOYEE_CSV_PATH = "data/employee.csv"
EMPLOYEE_PHOTO_DIR = "data/employee_photos"
os.makedirs("data", exist_ok=True)
os.makedirs(EMPLOYEE_PHOTO_DIR, exist_ok=True)

# CSV 로드 함수
def load_employees():
    if os.path.exists(EMPLOYEE_CSV_PATH):
        return pd.read_csv(EMPLOYEE_CSV_PATH)
    else:
        return pd.DataFrame(columns=["고유ID", "직원이름", "사진경로"])

# CSV 저장 함수
def save_employees(df):
    df.to_csv(EMPLOYEE_CSV_PATH, index=False)

# 메인 UI 함수
def settings_users_ui():
    st.markdown("## 👤 사용자 관리")
    st.markdown("###  직원 등록")

    with st.form("employee_form", clear_on_submit=True):
        name = st.text_input("직원이름")
        photo = st.file_uploader("직원 사진", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("직원 등록")  # key 파라미터 제거

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

    st.markdown("###  직원 목록")
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
                # 삭제 버튼에도 고유 key가 필요하므로 행 인덱스 사용
                if st.button("삭제", key=f"delete_{i}"):
                    if os.path.exists(row["사진경로"]):
                        os.remove(row["사진경로"])
                    df_employees = df_employees[df_employees["고유ID"] != row["고유ID"]]
                    save_employees(df_employees)
                    st.success(f"{row['직원이름']} 님이 삭제되었습니다.")
                    st.rerun()
