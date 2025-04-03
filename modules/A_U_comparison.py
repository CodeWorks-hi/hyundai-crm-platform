# 고객 메인 대시보드     
    # 차량 비교

import streamlit as st
import pandas as pd
import os
from A_U_main import switch_page

# +-------------+
# | 전차종 모델보기 |
# +-------------+


# 데이터 로드 
@st.cache_data
def load_car_data():
    df_path = "data/hyundae_car_list.csv"
    if os.path.exists(df_path):
        return pd.read_csv(df_path)
    else:
        return pd.DataFrame()


def save_selected_model(model_name):
    df = pd.DataFrame([{"선택모델": model_name}])
    df.to_csv("data/selected_car.csv", index=False)


def comparison_ui():
    if st.button("← 유저 메인으로 돌아가기", key="back_to_user_main"):
        st.session_state.current_page = "A_U_main"
        st.rerun()

    df = load_car_data()
    if df.empty:
        st.error("차량 데이터를 불러올 수 없습니다.")
        return

    col2, col4, col3 = st.columns([3, 0.2, 1])
    대표모델 = df.sort_values(by="기본가격").drop_duplicates(subset=["모델명"])

    with col2:
        st.markdown("### 전체 차량 모델")
        for i in range(0, len(대표모델), 3):
            row = 대표모델.iloc[i:i+3]
            cols = st.columns(3)

            for col_index, (col, (_, item)) in enumerate(zip(cols, row.iterrows())):
                with col:
                    st.markdown(
                        f"""
                        <div style="border:1px solid #ddd; border-radius:12px; padding:10px; text-align:center;
                                    box-shadow: 2px 2px 8px rgba(0,0,0,0.06); height: 330px;">
                            <div style="height:180px; background:#fff; display:flex; align-items:center; justify-content:center;">
                                <img src="{item['img_url']}" 
                                    style="height:140px; width:auto; object-fit:contain; max-width: 100%;" />
                            </div>
                            <div style="margin-top: 10px; font-weight:bold; font-size:16px;">{item['모델명']}</div>
                            <div style="color:gray;">{int(item['기본가격']):,}원부터 ~</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    key_val = f"선택_{item['모델명']}_{i}_{col_index}"
                    if st.button("이 차량 선택", key=key_val):
                        save_selected_model(item["모델명"])
                        switch_page("A_U_detail")
            #                     if st.button("이동", key="btn_event"):
            # switch_page("A_U_event")

    with col4:
        pass

    with col3:
        st.markdown("### 차량 정보")
        if "선택차량" in st.session_state:
            car = st.session_state["선택차량"]
            st.image(car.get("img_url", ""), use_container_width=True)
            st.markdown(f"**{car.get('모델명', '')} {car.get('트림명', '')}**")

            가격 = car.get("기본가격")
            가격표시 = f"{int(가격):,}원" if pd.notna(가격) else ""
            st.markdown(f"가격: {가격표시}")

            if st.button("판매 등록으로 이동"):
                st.session_state.current_page = "판매 등록"
                st.rerun()

            st.markdown("---")
            st.markdown("**세부 정보**")
            for col in ['연료구분', '배기량', '공차중량', '연비', '차량형태', '차량구분', '탑승인원']:
                value = car.get(col)
                st.markdown(f"- {col}: {value if pd.notna(value) else ''}")
        else:
            st.info("선택된 차량이 없습니다.")


# ▶️ 앱 진입점
def app():
    page = st.session_state.get("current_page", "A_U_main")

    if page == "A_U_main":
        comparison_ui()

    elif page == "A_U_detail":
        from modules.A_U_detail import detail_ui
        detail_ui()
# 상세 화면은 A_U_detail.py 내의 detail_ui 함수를 호출        
#     elif page == "A_U_detail":
#         import modules.A_U_detail as detail
#         detail.detail_ui()

