# 고객 메인 대시보드     
# 차량 비교

import streamlit as st
import pandas as pd
import os
from A_U_main import switch_page
from streamlit.components.v1 import html

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
    df = load_car_data()
    if df.empty:
        st.error("차량 데이터를 불러올 수 없습니다.")
        return

    col2, col4, col3 = st.columns([4, 0.1, 0.7])
    대표모델 = df.sort_values(by="기본가격").drop_duplicates(subset=["모델명"])

    with col2:
        st.markdown("### 전체 차량 모델")
        for i in range(0, len(대표모델), 4):
            row = 대표모델.iloc[i:i+4]
            cols = st.columns(4)

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
                        st.session_state["선택차량"] = item.to_dict()


    with col4:
        pass

    with col3:
        pass  # 차량 정보는 col3에 표시하지 않고, 별도 박스에 표시

    if "선택차량" in st.session_state:
        car = st.session_state["선택차량"]
        st.markdown(f"""
            <style>
            #car-info-box {{
                position: fixed;
                top: 150px;
                right: 30px;
                width: 320px;
                z-index: 999;
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 12px;
                padding: 16px;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
                font-family: sans-serif;
            }}
            </style>
            <div id="car-info-box">
                <img src="{car.get('img_url', '')}" style="width:100%; border-radius:8px;" />
                <h4 style="margin-top:10px;">{car.get('모델명', '')} {car.get('트림명', '')}</h4>
                <p><strong>가격:</strong> {int(car.get('기본가격', 0)):,}원</p>
                <hr />
                <p><strong>연료구분:</strong> {car.get('연료구분','')}</p>
                <p><strong>배기량:</strong> {car.get('배기량','')}</p>
                <p><strong>공차중량:</strong> {car.get('공차중량','')}</p>
                <p><strong>연비:</strong> {car.get('연비','')}</p>
                <p><strong>차량형태:</strong> {car.get('차량형태','')}</p>
                <p><strong>차량구분:</strong> {car.get('차량구분','')}</p>
                <p><strong>탑승인원:</strong> {car.get('탑승인원','')}</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("선택된 차량이 없습니다.")
