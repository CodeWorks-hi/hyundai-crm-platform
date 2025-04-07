import streamlit as st
import os
import pandas as pd


def consult_ui():
    if "wait_page" not in st.session_state: st.session_state["wait_page"] = 0
    if "done_page" not in st.session_state: st.session_state["done_page"] = 0
    if "visit_page" not in st.session_state: st.session_state["visit_page"] = 0

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
                    date = st.date_input("희망 상담 날짜")
                with col4:
                    time = st.time_input("희망 상담 시간")

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
                        "완료여부": 0,
                        "답변내용": "-",
                        "상담내용": "-",
                        "상담태그": "-",
                        "고객피드백": "-",
                        "목적": "방문"
                    }

                    df_path = "data/consult_log.csv"
                    if os.path.exists(df_path):
                        df = pd.read_csv(df_path)
                        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                    else:
                        df = pd.DataFrame([new_data])

                    df.to_csv(df_path, index=False)
                    st.success("방문예약 신청이 되었습니다.")

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
                    date = st.date_input("문의 날짜", key="inq_date", disabled=True)
                with col4:
                    time = st.time_input("문의 시간", key="inq_time", disabled=True)

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
                        "완료여부": 0,
                        "답변내용": "-",
                        "상담내용": "-",
                        "상담태그": "-",
                        "고객피드백": "-",
                        "목적": "문의"
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
    consult_list, spacer1, consult_true, spacer2, consult_visit, spacer3 ,consult_visit_True = st.columns([1, 0.02, 1, 0.02, 1, 0.02, 1])
    with spacer1:
        st.markdown("<div style='height:100%; border-left:1px solid #ddd;'></div>", unsafe_allow_html=True)
    with spacer2:
        st.markdown("<div style='height:100%; border-left:1px solid #ddd;'></div>", unsafe_allow_html=True)
    with spacer3:
        st.markdown("<div style='height:100%; border-left:1px solid #ddd;'></div>", unsafe_allow_html=True)

    # 상담 내역 표시
    df_path = "data/consult_log.csv"
    if os.path.exists(df_path):
        df = pd.read_csv(df_path)
        if "만족도" not in df.columns:
            df["만족도"] = ""
        if "답변내용" not in df.columns:
            df["답변내용"] = ""

        with consult_list:
            st.markdown("##### 상담 대기")
            wait_df = df[df["완료여부"] == False]
            per_page = 5
            total_wait_pages = (len(wait_df) - 1) // per_page + 1
            start = st.session_state["wait_page"] * per_page
            end = start + per_page
            wait_df_page = wait_df.iloc[start:end]
            for idx, row in wait_df_page.iterrows():
                st.markdown(f"""
                <div style='padding:6px 10px; border-bottom:1px solid #ddd;'>
                <b>성명:</b> {mask_name(row['이름'])}<br>
                <b>요청사항:</b> {row['요청사항']}<br>
                <b>진행상태:</b> 상담대기중
                </div>
                """, unsafe_allow_html=True)
                with st.expander("내용확인 및 삭제", expanded=False):
                    with st.form(f"view_wait_{idx}"):
                        input_name = st.text_input("이름 확인", key=f"wait_name_{idx}")
                        input_phone = st.text_input("전화번호 확인", key=f"wait_phone_{idx}")
                        col_open, col_delete = st.columns([1, 1])
                        with col_open:
                            open_clicked = st.form_submit_button("열기")
                        with col_delete:
                            delete_clicked = st.form_submit_button("삭제")

                        if input_name.strip() == str(row.get("이름", "")).strip() and input_phone.strip() == str(row.get("전화번호", "")).strip():
                            if open_clicked:
                                st.info(f"**상담내용:** {row['요청사항']}")
                                답변 = row['답변내용']
                                if pd.isna(답변) or str(답변).strip() == "":
                                    답변 = "답변대기중"
                                st.info(f"**답변내용:** {답변}")
                            elif delete_clicked:
                                df.drop(index=idx, inplace=True)
                                df.to_csv("data/consult_log.csv", index=False)
                                st.success("삭제되었습니다.")
                                st.rerun()
                        else:
                            if open_clicked or delete_clicked:
                                st.warning("정보가 일치하지 않습니다.")

            st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
            page_buttons = st.columns(7)

            with page_buttons[0]:
                if st.button("«", key="wait_first"):
                    st.session_state["wait_page"] = 0
                    st.rerun()

            start_page = max(0, st.session_state["wait_page"] - 2)
            end_page = min(total_wait_pages, start_page + 5)

            for i, page_num in enumerate(range(start_page, end_page)):
                with page_buttons[i + 1]:
                    if st.button(f"{page_num + 1}", key=f"wait_page_{page_num}"):
                        st.session_state["wait_page"] = page_num
                        st.rerun()

            with page_buttons[6]:
                if st.button("»", key="wait_last"):
                    st.session_state["wait_page"] = total_wait_pages - 1
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        with consult_true:
            st.markdown("##### 상담 완료 ")
            done_df = df[df["완료여부"] == True]
            total_done_pages = (len(done_df) - 1) // per_page + 1
            start = st.session_state["done_page"] * per_page
            end = start + per_page
            done_df_page = done_df.iloc[start:end]
            for idx, row in done_df_page.iterrows():
                st.markdown(f"""
                <div style='padding:6px 10px; border-bottom:1px solid #ddd;'>
                <b>성명:</b> {mask_name(row['이름'])}<br>
                <b>요청사항:</b> {row['요청사항']}<br>
                <b>진행상태:</b> 상담완료
                </div>
                """, unsafe_allow_html=True)
                with st.expander("내용확인 및 삭제", expanded=False):
                    with st.form(f"view_done_{idx}"):
                        input_name = st.text_input("이름 확인", key=f"done_name_{idx}")
                        input_phone = st.text_input("전화번호 확인", key=f"done_phone_{idx}")
                        col_open, col_delete = st.columns([1, 1])
                        with col_open:
                            open_clicked = st.form_submit_button("열기")
                        with col_delete:
                            delete_clicked = st.form_submit_button("삭제")

                        if input_name.strip() == str(row.get("이름", "")).strip() and input_phone.strip() == str(row.get("전화번호", "")).strip():
                            if open_clicked:
                                st.info(f"**상담내용:** {row['요청사항']}")
                                답변 = row['답변내용']
                                if pd.isna(답변) or str(답변).strip() == "":
                                    답변 = "답변대기중"
                                st.info(f"**답변내용:** {답변}")
                                # st.text_area("고객 피드백", key=f"feedback_{idx}")
                                # if st.form_submit_button("고객 피드백 제출"):
                                #     pass
                            elif delete_clicked:
                                df.drop(index=idx, inplace=True)
                                df.to_csv("data/consult_log.csv", index=False)
                                st.success("삭제되었습니다.")
                                st.rerun()
                        else:
                            if open_clicked or delete_clicked:
                                st.warning("정보가 일치하지 않습니다.")

            st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
            page_buttons = st.columns(7)

            with page_buttons[0]:
                if st.button("«", key="done_first"):
                    st.session_state["done_page"] = 0
                    st.rerun()

            start_page = max(0, st.session_state["done_page"] - 2)
            end_page = min(total_done_pages, start_page + 5)

            for i, page_num in enumerate(range(start_page, end_page)):
                with page_buttons[i + 1]:
                    if st.button(f"{page_num + 1}", key=f"done_page_{page_num}"):
                        st.session_state["done_page"] = page_num
                        st.rerun()

            with page_buttons[6]:
                if st.button("»", key="done_last"):
                    st.session_state["done_page"] = total_done_pages - 1
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        with consult_visit:
            st.markdown("##### 방문 신청 목록")
            visit_df = df[(df["완료여부"] == False) & (df["목적"] == "방문")]
            total_visit_pages = (len(visit_df) - 1) // per_page + 1
            start = st.session_state["visit_page"] * per_page
            end = start + per_page
            visit_df_page = visit_df.iloc[start:end]
            for idx, row in visit_df_page.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style='padding:6px 10px; border-bottom:1px solid #ddd;'>
                    <b>성명:</b> {mask_name(row['이름'])}<br>
                    <b>방문예정일:</b> {row['상담날짜']}
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("예약 취소", expanded=False):
                        with st.form(f"cancel_visit_{idx}"):
                            input_name = st.text_input("이름 확인", key=f"cancel_name_{idx}")
                            input_phone = st.text_input("전화번호 확인", key=f"cancel_phone_{idx}")
                            cancel_clicked = st.form_submit_button("예약 취소")
                            if cancel_clicked:
                                if input_name.strip() == str(row.get("이름", "")).strip() and input_phone.strip() == str(row.get("전화번호", "")).strip():
                                    df.drop(index=idx, inplace=True)
                                    df.to_csv("data/consult_log.csv", index=False)
                                    st.success("예약이 취소되었습니다.")
                                    st.rerun()
                                else:
                                    st.warning("정보가 일치하지 않습니다.")

            st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
            page_buttons = st.columns(7)

            with page_buttons[0]:
                if st.button("«", key="visit_first"):
                    st.session_state["visit_page"] = 0
                    st.rerun()

            start_page = max(0, st.session_state["visit_page"] - 2)
            end_page = min(total_visit_pages, start_page + 5)

            for i, page_num in enumerate(range(start_page, end_page)):
                with page_buttons[i + 1]:
                    if st.button(f"{page_num + 1}", key=f"visit_page_{page_num}"):
                        st.session_state["visit_page"] = page_num
                        st.rerun()

            with page_buttons[6]:
                if st.button("»", key="visit_last"):
                    st.session_state["visit_page"] = total_visit_pages - 1
                    st.rerun()
        with consult_visit_True:
            st.markdown("##### 방문 완료")
            visit_df = df[(df["완료여부"] == True) & (df["목적"] == "방문")]
            per_page = 5
            if "visit_done_page" not in st.session_state:
                st.session_state["visit_done_page"] = 0

            total_visit_pages = (len(visit_df) - 1) // per_page + 1
            start = st.session_state["visit_done_page"] * per_page
            end = start + per_page
            visit_df_page = visit_df.iloc[start:end]

            for idx, row in visit_df_page.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style='padding:6px 10px; border-bottom:1px solid #ddd;'>
                    <b>성명:</b> {mask_name(row['이름'])}<br>
                    <b>방문일:</b> {row['상담날짜']}
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("만족도 조사", expanded=False):
                        with st.form(f"satis_{idx}"):
                            input_name = st.text_input("이름 확인", key=f"done_name_{idx}")
                            input_phone = st.text_input("전화번호 확인", key=f"done_phone_{idx}")
                            rating = st.slider("⭐ 상담 만족도 (1~5점)", 1, 5, 3, key=f"rating_{idx}")
                            if st.form_submit_button("고객 피드백 제출"):
                                if input_name.strip() == str(row.get("이름", "")).strip() and input_phone.strip() == str(row.get("전화번호", "")).strip():
                                    df.at[idx, "고객피드백"] = rating
                                    df.to_csv("data/consult_log.csv", index=False)
                                    st.success("피드백이 제출되었습니다.")
                                    st.rerun()
                                else:
                                    st.warning("정보가 일치하지 않습니다.")

            st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
            page_buttons = st.columns(7)

            with page_buttons[0]:
                if st.button("«", key="visit_done_first"):
                    st.session_state["visit_done_page"] = 0
                    st.rerun()

            start_page = max(0, st.session_state["visit_done_page"] - 2)
            end_page = min(total_visit_pages, start_page + 5)

            for i, page_num in enumerate(range(start_page, end_page)):
                with page_buttons[i + 1]:
                    if st.button(f"{page_num + 1}", key=f"visit_done_page_{page_num}"):
                        st.session_state["visit_done_page"] = page_num
                        st.rerun()

            with page_buttons[6]:
                if st.button("»", key="visit_done_last"):
                    st.session_state["visit_done_page"] = total_visit_pages - 1
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)