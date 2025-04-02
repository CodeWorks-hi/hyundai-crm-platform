import streamlit as st

def test_drive_ui():
    if st.button("← 유저 메인으로 돌아가기", key="back_to_user_main"):
        st.session_state.current_page = "user_main"
        st.rerun()
        
    st.title("시승 신청")

    st.markdown("원하시는 차량을 직접 경험해보세요. 아래 정보를 입력해 주시면 시승 상담을 도와드리겠습니다.")

    with st.form("test_drive_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("성함")
            phone = st.text_input("연락처", placeholder="010-0000-0000")
            preferred_date = st.date_input("시승 희망 날짜")

        with col2:
            car_model = st.selectbox("시승 희망 차량", ["아이오닉5", "팰리세이드", "그랜저", "캐스퍼"])
            location = st.selectbox("시승 지점", ["서울 강남지점", "인천 부평지점", "부산 해운대지점"])
            time_slot = st.selectbox("희망 시간대", ["오전 (9시~12시)", "오후 (1시~5시)", "저녁 (6시~8시)"])

        request_note = st.text_area("요청사항 (선택)", height=100)

        submitted = st.form_submit_button("시승 신청하기")

        if submitted:
            st.success("✅ 시승 신청이 완료되었습니다. 담당자가 곧 연락드릴 예정입니다.")
            # 👉 여기에 추후 DB 저장 or 이메일 전송 등의 로직 연결 가능