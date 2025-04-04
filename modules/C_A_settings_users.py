# 사용자 관리
# 직원 등록, 삭제, 수정, 조회
# 직원 등록시 사진도 함께 등록
# 직원 등록시 사진은 저장되고, 사진 경로만 DB에 저장
# 직원 등록시 사진은 /data/employee_photos/ 디렉토리에 저장
# 직원 등록시 고유ID는 uuid.uuid4()로 생성
# 직원 목록은 /data/employee.csv 파일에 저장
# 직원 목록은 pandas DataFrame으로 관리
# 직원 목록은 고유ID, 직원이름,"사번", 사진경로로 구성
# 직원 목록은 등록된 직원이 없을 경우에 대한 예외 처리
# 데이터 동기화 상태


import os
import uuid
import streamlit as st
import pandas as pd
import numpy as np
import cv2
import face_recognition
import mediapipe as mp
from PIL import Image

# 경로 설정
EMPLOYEE_CSV_PATH = "data/employee.csv"
EMPLOYEE_PHOTO_DIR = "data/employee_photos"
os.makedirs("data", exist_ok=True)
os.makedirs(EMPLOYEE_PHOTO_DIR, exist_ok=True)

# 직원 데이터 로드
def load_employees():
    if os.path.exists(EMPLOYEE_CSV_PATH):
        df = pd.read_csv(EMPLOYEE_CSV_PATH)
        expected_columns = ["고유ID", "직원이름", "사번", "사진경로", "인코딩"]
        for col in expected_columns:
            if col not in df.columns:
                df[col] = np.nan
        return df[expected_columns]
    else:
        return pd.DataFrame(columns=["고유ID", "직원이름", "사번", "사진경로", "인코딩"])

# 직원 데이터 저장
def save_employees(df):
    df.to_csv(EMPLOYEE_CSV_PATH, index=False)

# 얼굴 인코딩
def encode_face(img_path):
    image = face_recognition.load_image_file(img_path)
    encodings = face_recognition.face_encodings(image)
    return encodings[0] if encodings else None

# 얼굴 비교
def is_same_person(new_encoding, stored_encodings, names, tolerance=0.45):
    results = face_recognition.compare_faces(stored_encodings, new_encoding, tolerance)
    if True in results:
        idx = results.index(True)
        return names[idx]
    return None

# Streamlit UI
def users_ui():
    st.markdown("## 👤 사용자 관리")
    st.markdown("### 직원 등록")

    with st.form("employee_form", clear_on_submit=True):
        name = st.text_input("직원이름")
        emp_number = st.text_input("사번")  
        photo = st.file_uploader("직원 사진", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("직원 등록")

        if submitted:
            if name and emp_number and photo:
                df = load_employees()
                if emp_number in df["사번"].values:
                    st.warning(f"이미 등록된 사번입니다: {emp_number}")
                else:
                    new_id = str(uuid.uuid4())
                    ext = os.path.splitext(photo.name)[1]
                    save_filename = f"{new_id}{ext}"
                    save_path = os.path.join(EMPLOYEE_PHOTO_DIR, save_filename)

                    with open(save_path, "wb") as f:
                        f.write(photo.getbuffer())

                    encoding = encode_face(save_path)
                    if encoding is not None:
                        new_row = pd.DataFrame([{
                            "고유ID": new_id,
                            "직원이름": name,
                            "사번": emp_number,
                            "사진경로": save_path,
                            "인코딩": encoding.tolist()
                        }])
                        df = pd.concat([df, new_row], ignore_index=True)
                        save_employees(df)
                        st.success(f"{name} 님이 등록되었습니다.")
                    else:
                        os.remove(save_path)
                        st.warning("❌ 사진에서 얼굴을 인식할 수 없습니다.")
            else:
                st.warning("이름, 사번, 사진을 모두 입력해주세요.")

    # 직원 목록 보기
    st.markdown("### 직원 목록")
    df_employees = load_employees()

    if df_employees.empty:
        st.info("등록된 직원이 없습니다.")
    else:
        for i, row in df_employees.iterrows():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{row['직원이름']}** (사번: {row['사번']})")
                st.caption(f"ID: {row['고유ID']}")
            with col2:
                if os.path.exists(row["사진경로"]):
                    st.image(row["사진경로"], width=100)
                else:
                    st.warning("❗ 사진 파일이 없습니다.")
            with col3:
                if st.button("삭제", key=f"delete_{i}"):
                    if os.path.exists(row["사진경로"]):
                        os.remove(row["사진경로"])
                    df_employees = df_employees[df_employees["고유ID"] != row["고유ID"]]
                    save_employees(df_employees)
                    st.success(f"{row['직원이름']} 님이 삭제되었습니다.")
                    st.rerun()

    # # 얼굴 매칭
    # st.markdown("### 얼굴 사진 일치 여부 확인")
    # upload = st.file_uploader("비교할 얼굴 사진을 업로드하세요", type=["jpg", "jpeg", "png"], key="match")

    # if upload:
    #     temp_path = os.path.join("temp.jpg")
    #     with open(temp_path, "wb") as f:
    #         f.write(upload.getbuffer())

    #     test_encoding = encode_face(temp_path)

    #     if test_encoding is None:
    #         st.error("❌ 사진에서 얼굴을 인식할 수 없습니다.")
    #     else:
    #         encodings = df_employees["인코딩"].dropna().apply(eval).tolist()
    #         names = df_employees["직원이름"].tolist()
    #         result = is_same_person(test_encoding, encodings, names)

    #         if result:
    #             st.success(f"✅ 등록된 직원 중 **{result}** 님과 얼굴이 일치합니다.")
    #         else:
    #             st.warning("⚠️ 일치하는 직원이 없습니다.")

    #     os.remove(temp_path)

    # MediaPipe 얼굴 탐지 (웹캠)
    # st.markdown("###  실시간 웹캠 얼굴 탐지 (MediaPipe)")
    # if st.button("📷 얼굴 탐지 실행"):
    #     mp_face = mp.solutions.face_detection.FaceDetection(model_selection=0)
    #     cap = cv2.VideoCapture(0)
    #     st.info("카메라에서 한 장의 이미지를 캡처 중입니다...")

    #     ret, frame = cap.read()
    #     if ret:
    #         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #         results = mp_face.process(rgb_frame)

    #         if results.detections:
    #             for detection in results.detections:
    #                 print("Face detected with score:", detection.score)
    #         else:
    #             print("No face detected.")

    #     cap.release()