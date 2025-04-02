import streamlit as st

def detail_ui():
    st.title("차량 상세정보")

    if "선택차량" not in st.session_state:
        st.warning("선택된 차량이 없습니다.")
        return

    car = st.session_state["선택차량"]
    st.image(car.get("img_url", ""), use_container_width=True)
    st.markdown(f"### {car.get('모델명', '')} {car.get('트림명', '')}")
    st.markdown(f"**가격:** {int(car.get('기본가격', 0)):,}원")

    st.markdown("**세부 제원**")
    for col in ['연료구분', '배기량', '공차중량', '연비', '차량형태', '차량구분', '탑승인원']:
        value = car.get(col)
        st.markdown(f"- {col}: {value if pd.notna(value) else ''}")

    if st.button("← 차량 비교로 돌아가기"):
        st.session_state["current_page"] = "home"
        st.rerun()
