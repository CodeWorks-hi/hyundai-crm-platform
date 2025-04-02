import streamlit as st
import pandas as pd
import os
from datetime import datetime

def consult_ui():
    st.title("📞 상담 예약")

    # 입력 폼
    with st.form("consult_form", clear_on_submit=True):
        name = st.text_input("이름")
        phone = st.text_input("전화번호")
        date = st.date_input("상담 날짜")
        time = st.time_input("상담 시간")
        content = st.text_area("상담 내용")

        submitted = st.form_submit_button("예약하기")

        if submitted:
            new_data = {
                "이름": name,
                "전화번호": phone,
                "상담날짜": date.strftime("%Y-%m-%d"),
                "상담시간": time.strftime("%H:%M"),
                "상담내용": content,
                "등록일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            df_path = "data/consult_log.csv"
            if os.path.exists(df_path):
                df = pd.read_csv(df_path)
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            else:
                df = pd.DataFrame([new_data])

            df.to_csv(df_path, index=False)
            st.success("상담이 예약되었습니다.")
