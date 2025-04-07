import streamlit as st
import pandas as pd
import joblib
import numpy as np
import os
import time


# 커스텀 메시지 함수: 이미지와 배경, 글자색을 지정하여 눈에 띄게 만듭니다.
def custom_message(message, msg_type="success"):
    if msg_type == "success":
        image_url = "https://img.icons8.com/color/48/000000/checked--v1.png"
        background = "#d4edda"
        color = "#155724"
    elif msg_type == "info":
        image_url = "https://img.icons8.com/color/48/000000/info--v1.png"
        background = "#d1ecf1"
        color = "#0c5460"
    elif msg_type == "error":
        image_url = "https://img.icons8.com/color/48/000000/high-importance.png"
        background = "#f8d7da"
        color = "#721c24"
    elif msg_type == "promotion1":
        image_url = "https://img.icons8.com/color/48/000000/gift--v1.png"
        background = "#fff4e5"
        color = "#8a6d3b"
    elif msg_type == "promotion2":
        image_url = "https://img.icons8.com/color/48/000000/prize.png"
        background = "#fff4e5"
        color = "#8a6d3b"
    elif msg_type == "question":
        image_url = "https://img.icons8.com/color/48/000000/help.png"
        background = "#e2e3e5"
        color = "#383d41"
    else:
        image_url = ""
        background = "#ffffff"
        color = "#000000"
    html_string = f'''
    <div style="display: flex; align-items: center; padding: 15px; border-radius: 8px; background-color: {background}; margin: 10px 0;">
        <img src="{image_url}" style="width: 48px; height: 48px; margin-right: 15px;">
        <span style="font-size: 22px; font-weight: bold; color: {color};">{message}</span>
    </div>
    '''
    st.markdown(html_string, unsafe_allow_html=True)

def demand_forecast_ui():
    if "고객정보" not in st.session_state or not isinstance(st.session_state["고객정보"], dict):
        st.session_state["고객정보"] = {"나이": "", "성별": "", "거주지역": ""}
    else:
        st.session_state["고객정보"].setdefault("나이", "")
        st.session_state["고객정보"].setdefault("성별", "")
        st.session_state["고객정보"].setdefault("거주지역", "")

    if "recom_budget" not in st.session_state:
        st.session_state["recom_budget"] = 1000

    c_df = pd.read_csv("data/domestic_customer_data.csv")
    df = pd.read_csv("data/hyundae_car_list.csv")
    df = df.loc[df["브랜드"] != "기아", :]


    st.markdown("""
    <div style='background-color: #ffffff; padding: 10px 10px 10px 10px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); margin-bottom: 10px;'>
        <h3 style='color: #003366; margin-bottom: 10px;'> 고객 기본 정보 입력 </h3>
    """, unsafe_allow_html=True)
    default_budget = st.session_state["recom_budget"]
    default_gender = st.session_state["고객정보"]["성별"]
    gender_options = ["남성", "여성"]
    if default_gender not in gender_options:
        default_gender = "남성"
    default_region = st.session_state["고객정보"]["거주지역"]
    default_age = st.session_state["고객정보"]["나이"]                               

    try:
        default_age = int(default_age)
    except (ValueError, TypeError):
        default_age = 30

    budget = st.number_input("구매 예산 (만원)", value=default_budget, step=500)
    gender = st.selectbox("성별", gender_options, index=gender_options.index(default_gender))
    age = st.number_input("나이", min_value=1, max_value=100, step=1, value=default_age)
    regions = [
        '인천광역시', '광주광역시', '부산광역시', '전라남도', '경기도', '울산광역시', '서울특별시', '경상남도',
        '전라북도', '충청북도', '경상북도', '강원도', '충청남도', '대구광역시', '대전광역시', '제주특별자치도'
    ]
    if default_region not in regions:
        default_region = "서울특별시"
    region = st.selectbox("거주 지역", regions, index=regions.index(default_region))
    preference = st.selectbox("선호 브랜드", ["현대", "제네시스"])

    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    if st.button("추천 받기"):
        with st.spinner("추천 결과를 생성 중입니다..."):
            time.sleep(3)
            custom_message("추천 결과가 생성되었습니다.", "success")

        region_list = {
            '강원도': [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            '경기도': [0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            '경상남도': [0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
            '경상북도': [0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
            '광주광역시': [0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
            '대구광역시': [0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],
            '대전광역시': [0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
            '부산광역시': [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
            '서울특별시': [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
            '울산광역시': [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0],
            '인천광역시': [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
            '전라남도': [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0],
            '전라북도': [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0],
            '제주특별자치도': [0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0],
            '충청남도': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0],
            '충청북도': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]
        }

        gender_list = {
            "남": [1,0],
            "여": [0,1]
        }

        brand_list = {
            "제네시스": [1,0],
            "현대": [0,1]
        }

        user_data = np.hstack([
            age,
            budget * 10000,
            gender_list.get(gender, [0, 0]),
            region_list.get(region, [0]*16),
            brand_list.get(preference, [0, 0])
        ]).reshape(1, -1)[0]
        user_data = np.array(user_data).reshape(1, 22)

       
        dtc = joblib.load(f"model/DecisionTree Model.pkl")
        gbc = joblib.load(f"model/GradientBoosting Model.pkl")
        lgb = joblib.load(f"model/LightGBM Model.pkl")

        recom_list = []
        recom_list.append(dtc.predict(user_data)[0])
        recom_list.append(gbc.predict(user_data)[0])
        recom_list.append(lgb.predict(user_data)[0])
        recom_list = list(set(recom_list))
        
        min_price_list = {
            'G70': 4035,
            'G80': 5775,
            'G90': 9400,
            'GV60': 6731,
            'GV70': 5586,
            'GV80': 6886,
            '그랜저': 3706,
            '넥쏘': 6895,
            '베뉴': 2114,
            '스타리아': 3209,
            '쏘나타': 2798,
            '아반떼': 2114,
            '아이오닉5': 5250,
            '아이오닉6': 5200,
            '아이오닉9': 5800,
            '캐스퍼': 1390,
            '투싼': 2860,
            '펠리세이드': 4269
        }

        recom_list = [i for i in recom_list if int(min_price_list[i]) <= budget]

        tab1, tab2 = st.tabs(["추천 차량 리스트", "전기차 추천"])

        with tab1:
            if len(recom_list) != 0:
                st.subheader("추천 차량 리스트")
                columns_per_row = 3
                num_cars = len(recom_list)

                header_titles = [f"추천 차량 {i+1}" for i in range(min(columns_per_row, num_cars))]
                table_header = "| " + " | ".join(header_titles) + " |\n"
                table_header += "| " + " | ".join(["---"] * min(columns_per_row, num_cars)) + " |\n"

                img_rows = []
                text_rows = []

                
                for idx, car_name in enumerate(recom_list):
                    image_url = df.loc[df['모델명'] == car_name, 'img_url'].to_numpy()[0]
                    img_tag = f'<img src="{image_url}" width="320">' if image_url else "이미지 없음"
                    price = min_price_list.get(car_name, '가격 정보 없음')
                    mileage = df.loc[df['모델명'] == car_name, '연비'].to_numpy()[0]
                    engine = df.loc[df['모델명'] == car_name, '배기량'].to_numpy()[0]
                    emission = df.loc[df['모델명'] == car_name, 'CO2배출량'].to_numpy()[0]
                    summary = ""
                    if df.loc[df['모델명'] == car_name, '연료구분'].to_numpy()[0] == "전기":
                        summary = f"**{car_name}**<br>가격: {price}만원~<br>연비: {mileage}km/kWh"
                    else:
                        summary = f"**{car_name}**<br>가격: {price}만원~<br>연비: {mileage}km/L<br>배기량: {engine}cc<br>CO2 배출량: {emission}g/km"
                    img_rows.append(img_tag)
                    text_rows.append(summary)
                    if (idx + 1) % columns_per_row == 0 or idx == num_cars - 1:
                        st.markdown("""
                        <div style='padding: 25px; background-color: #ffffff; border-radius: 10px; box-shadow: 0 3px 10px rgba(0,0,0,0.06); margin-bottom: 20px;'>
                        """, unsafe_allow_html=True)

                        img_row = "| " + " | ".join(img_rows) + " |\n"
                        text_row = "| " + " | ".join(text_rows) + " |\n"
                        table_header += img_row + text_row
                        st.markdown(table_header, unsafe_allow_html=True)

                        st.markdown("</div>", unsafe_allow_html=True)
                        img_rows, text_rows = [], []
            else:
                custom_message("😢 죄송합니다. 예산 내에 맞는 차량이 없습니다. 조건을 확인해주세요!", "error")
                custom_message("🔍 전기차는 어떠신가요? '전기차 추천' 탭을 클릭해 확인해보세요!", "question")
        
        with tab2:
            # 전기차 보조금 데이터 로드
            ec_df = pd.read_csv("data/ec_gift.csv")
            ec_dict = ec_df.set_index("지역구분")["보조금/승용(만원)"].to_dict()
            elec_car_compen = {k: int(v * 10000) for k, v in ec_dict.items()}

            def comma(x):
                return format(x, ',')
            
            compen = elec_car_compen[region]

            recom_elec = df.loc[(df["기본가격"] <= budget * 10000 + compen) & (df["연료구분"].isin(["전기", "하이브리드"])), "모델명"].unique()[:3]
            with st.spinner("추천 결과를 생성 중입니다..."):
                time.sleep(3)
                custom_message(
                    f"""
                    ✨ 최적의 전기차 추천 리스트가 준비되었습니다! 
                    <span style="font-size: 16px; color: #555;">\n\n(💡 {region} 지역의 전기차 보조금: **{comma(elec_car_compen[region])}원**)</span>
                    """,
                    "info"
                )

            columns_per_row = 3  
            num_cars = len(recom_elec)
            if num_cars > 0:
                st.subheader("전기차 추천 리스트")
                header_titles = [f"추천 차량 {i+1}" for i in range(min(columns_per_row, num_cars))]
                table_header = "| " + " | ".join(header_titles) + " |\n"
                table_header += "| " + " | ".join(["---"] * min(columns_per_row, num_cars)) + " |\n"
                img_rows = []
                text_rows = []
                for idx, car_name in enumerate(recom_elec):
                    image_url = df.loc[(df['모델명'] == car_name) & ((df['연료구분'] == '전기') | (df['연료구분'] == '하이브리드')), 'img_url'].to_numpy()[0]
                    img_tag = f'<img src="{image_url}" width="320">' if image_url else "이미지 없음"
                    price = min_price_list.get(car_name, '가격 정보 없음')
                    mileage = df.loc[(df['모델명'] == car_name) & ((df['연료구분'] == '전기') | (df['연료구분'] == '하이브리드')), '연비'].to_numpy()[0]
                    summary = f"**{car_name}**<br>가격: {price}만원~<br>연비: {mileage}km/kWh"
                    img_rows.append(img_tag)
                    text_rows.append(summary)
                    if (idx + 1) % columns_per_row == 0 or idx == num_cars - 1:
                        st.markdown("""
                        <div style='padding: 25px; background-color: #ffffff; border-radius: 10px; box-shadow: 0 3px 10px rgba(0,0,0,0.06); margin-bottom: 20px;'>
                        """, unsafe_allow_html=True)

                        img_row = "| " + " | ".join(img_rows) + " |\n"
                        text_row = "| " + " | ".join(text_rows) + " |\n"
                        table_header += img_row + text_row
                        st.markdown(table_header, unsafe_allow_html=True)

                        st.markdown("</div>", unsafe_allow_html=True)
                        img_rows, text_rows = [], []
            else:
                custom_message("😢 죄송합니다. 예산 내에 맞는 차량이 없습니다. 조건을 확인해주세요!", "error")

    st.markdown("###### ")

    with st.expander("🗂 원본 데이터 확인", expanded=False):
        tab1, tab2 = st.tabs(["차량 판매 기록", "차량 상세 정보"])
        with tab1:
            base_df = pd.read_csv("data/domestic_customer_data.csv")
            st.dataframe(base_df, hide_index=True, use_container_width=True)
        with tab2:
            base_df = pd.read_csv("data/hyundae_car_list.csv")
            st.dataframe(base_df, hide_index=True, use_container_width=True)