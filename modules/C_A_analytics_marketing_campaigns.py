import streamlit as st
import pandas as pd
import os
from datetime import datetime

CSV_PATH = "data/campaign_list.csv"
IMAGE_DIR = "images/event"
os.makedirs(IMAGE_DIR, exist_ok=True)

def render_campaign_register():
    st.subheader("이벤트 등록")

    with st.form("register_campaign_form"):
        event_name = st.text_input("이벤트명")
        target = st.text_area("대상")
        benefit = st.text_area("혜택")
        method = st.text_area("참여 방법")
        duration = st.text_input("이벤트 기간 (예: 2025-04-10 ~ 2025-05-10)")
        strategy_type = st.selectbox("전략 분류", ["유류비", "시승", "라이프스타일", "장기보상", "제휴마케팅", "방문상담"])
        is_active = st.checkbox("활성화 여부", value=True)

        st.markdown("이미지는 **png 파일만 업로드 가능**하며, `images/event/` 경로에 저장됩니다.")
        uploaded_file = st.file_uploader("이벤트배너 이미지 업로드 (PNG)", type=["png"])

        submitted = st.form_submit_button("이벤트 등록")

        if submitted and event_name:
            image_path = ""
            if uploaded_file:
                file_name = uploaded_file.name.replace(" ", "_").lower()
                image_path = os.path.join(IMAGE_DIR, file_name)
                with open(image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            new_row = pd.DataFrame([{
                "이벤트명": event_name,
                "대상": target,
                "혜택": benefit,
                "참여 방법": method,
                "기간": duration,
                "분류": strategy_type,
                "활성화": is_active,
                "이미지": image_path
            }])

            if os.path.exists(CSV_PATH):
                df = pd.read_csv(CSV_PATH)
                df = pd.concat([df, new_row], ignore_index=True)
            else:
                df = new_row

            df.to_csv(CSV_PATH, index=False)
            st.success("이벤트가 등록되었습니다.")
        elif submitted:
            st.warning("이벤트명을 입력해주세요.")


def render_campaign_manager():
    st.subheader("이벤트관리")

    filter_option = st.radio("이벤트 상태 필터", ["전체", "진행 중", "예정", "종료됨"], horizontal=True)

    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)

        today = datetime.today().date()
        df["시작일"] = df["기간"].str.split("~").str[0].str.strip()
        df["종료일"] = df["기간"].str.split("~").str[1].str.strip()
        df["시작일"] = pd.to_datetime(df["시작일"], errors="coerce").dt.date
        df["종료일"] = pd.to_datetime(df["종료일"], errors="coerce").dt.date

        if filter_option == "진행 중":
            df = df[(df["시작일"] <= today) & (df["종료일"] >= today)]
        elif filter_option == "예정":
            df = df[df["시작일"] > today]
        elif filter_option == "종료됨":
            df = df[df["종료일"] < today]

        for i, row in df.iterrows():
            with st.expander(f"{row['이벤트명']}"):
                st.markdown(f"- **기간**: {row['기간']}")
                st.markdown(f"- **대상**: {row['대상']}")
                st.markdown(f"- **혜택**: {row['혜택']}")
                st.markdown(f"- **참여 방법**: {row['참여 방법']}")
                st.markdown(f"- **전략 분류**: {row['분류']}")
                st.markdown(f"- **활성화 여부**: {'사용중' if row['활성화'] else '비활성'}")

                if "이미지" in row and pd.notna(row["이미지"]) and os.path.exists(row["이미지"]):
                    st.image(row["이미지"], width=300)

                col1, col2 = st.columns([0.3, 0.3])
                with col1:
                    if st.button("수정", key=f"edit_{i}"):
                        st.warning("✏️ 수정 기능은 현재 개발 중입니다.")
                with col2:
                    if st.button("삭제", key=f"delete_{i}"):
                        df.drop(i, inplace=True)
                        df.to_csv(CSV_PATH, index=False)
                        st.success("삭제되었습니다.")
                        st.rerun()
    else:
        st.info("등록된 캠페인이 없습니다.")
