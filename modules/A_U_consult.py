import streamlit as st
import os
import pandas as pd


def consult_ui():

    def mask_name(name):
        if len(name) >= 2:
            return name[0] + "*" + name[-1]
        return name

    left_form, right_form = st.columns(2)

    with left_form:
        with st.expander("방문 예약", expanded=True):
            with st.form("consult_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("이름")
                with col2:
                    phone = st.text_input("전화번호")

                col3, col4 = st.columns(2)
                with col3:
                    date = st.date_input("상담 날짜")
                with col4:
                    time = st.time_input("상담 시간")

                content = st.text_area("상담 내용")

                if content is None:
                    content = "-"

                submitted = st.form_submit_button("예약하기")

                if submitted:
                    new_data = {
                        "이름": name,
                        "전화번호": phone,
                        "상담날짜": date.strftime("%Y-%m-%d"),
                        "상담시간": time.strftime("%H:%M"),
                        "요청사항": content,
                        "담당직원": "홍길동",
                        "완료여부": False,
                        "상담내용": "-",
                        "상담태그": "-",
                        "고객피드백": "-"
                    }

                    df_path = "data/consult_log.csv"
                    if os.path.exists(df_path):
                        df = pd.read_csv(df_path)
                        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                    else:
                        df = pd.DataFrame([new_data])

                    df.to_csv(df_path, index=False)
                    st.success("상담이 예약되었습니다.")

    with right_form:
        with st.expander("문의하기", expanded=True):
            with st.form("inquiry_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("이름", key="inq_name")
                with col2:
                    phone = st.text_input("전화번호", key="inq_phone")

                col3, col4 = st.columns(2)
                with col3:
                    date = st.date_input("문의 날짜", key="inq_date")
                with col4:
                    time = st.time_input("문의 시간", key="inq_time")

                content = st.text_area("문의 내용", key="inq_content")

                if content is None:
                    content = "-"

                submitted = st.form_submit_button("문의하기")

                if submitted:
                    new_data = {
                        "이름": name,
                        "전화번호": phone,
                        "상담날짜": date.strftime("%Y-%m-%d"),
                        "상담시간": time.strftime("%H:%M"),
                        "요청사항": content,
                        "담당직원": "홍길동",
                        "완료여부": False,
                        "상담내용": "-",
                        "상담태그": "-",
                        "고객피드백": "-"
                    }

                    df_path = "data/consult_log.csv"
                    if os.path.exists(df_path):
                        df = pd.read_csv(df_path)
                        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                    else:
                        df = pd.DataFrame([new_data])

                    df.to_csv(df_path, index=False)
                    st.success("문의가 접수되었습니다.")

    st.markdown("---")
    consult_list, consult_true, consult_check = st.columns(3)

    # 상담 내역 표시
    df_path = "data/consult_log.csv"
    if os.path.exists(df_path):
        df = pd.read_csv(df_path)

        if "답변내용" not in df.columns:
            df["답변내용"] = ""

        with consult_list:
            st.markdown("#### 상담 대기중 목록")
            wait_df = df[df["완료여부"] == False]
            for idx, row in wait_df.iterrows():
                st.markdown(f"""
                <div style='padding:6px 10px; border-bottom:1px solid #ddd;'>
                <b>성명:</b> {mask_name(row['이름'])}<br>
                <b>요청사항:</b> {row['요청사항']}<br>
                <b>진행상태:</b> 상담대기중
                </div>
                """, unsafe_allow_html=True)
                with st.expander("열기", expanded=False):
                    with st.form(f"view_wait_{idx}"):
                        input_name = st.text_input("이름 확인", key=f"wait_name_{idx}")
                        input_phone = st.text_input("전화번호 확인", key=f"wait_phone_{idx}")
                        if st.form_submit_button("열기"):
                            if input_name.strip() == str(row.get("이름", "")).strip() and input_phone.strip() == str(row.get("전화번호", "")).strip():
                                st.info(f"**상담내용:** {row['요청사항']}")
                                답변 = row['답변내용']
                                if pd.isna(답변) or str(답변).strip() == "":
                                    답변 = "답변대기중"
                                st.info(f"**답변내용:** {답변}")
                            else:
                                st.warning("정보가 일치하지 않습니다.")

        with consult_true:
            st.markdown("#### 상담 완료 목록")
            done_df = df[df["완료여부"] == True]
            for idx, row in done_df.iterrows():
                st.markdown(f"""
                <div style='padding:6px 10px; border-bottom:1px solid #ddd;'>
                <b>성명:</b> {mask_name(row['이름'])}<br>
                <b>요청사항:</b> {row['요청사항']}<br>
                <b>진행상태:</b> 상담완료
                </div>
                """, unsafe_allow_html=True)
                with st.expander("열기", expanded=False):
                    with st.form(f"view_done_{idx}"):
                        input_name = st.text_input("이름 확인", key=f"done_name_{idx}")
                        input_phone = st.text_input("전화번호 확인", key=f"done_phone_{idx}")
                        if st.form_submit_button("열기"):
                            if input_name.strip() == str(row.get("이름", "")).strip() and input_phone.strip() == str(row.get("전화번호", "")).strip():
                                st.info(f"**상담내용:** {row['요청사항']}")
                                답변 = row['답변내용']
                                if pd.isna(답변) or str(답변).strip() == "":
                                    답변 = "답변대기중"
                                st.info(f"**답변내용:** {답변}")
                            else:
                                st.warning("정보가 일치하지 않습니다.")
