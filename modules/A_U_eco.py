import pandas as pd
import streamlit as st
import base64
import requests

# 이미지 URL을 Base64로 변환하는 함수
def encode_image_from_url_to_base64(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        img_data = response.content
        encoded_image = base64.b64encode(img_data).decode('utf-8')
        return encoded_image
    else:
        return None

def eco_ui():
    # 데이터 로드
    suso_gift = pd.read_csv('data/suso_gift.csv')
    ec_gift = pd.read_csv('data/ec_gift.csv')
    char = pd.read_csv('data/char.csv')
    car_list = pd.read_csv('data/hyundae_car_list.csv')

    # 타이틀
    st.title('전기차 및 수소차 구매보조금 조회')

    # 컬럼 나누기
    col1, col2 = st.columns([1, 1])

    # 왼쪽: 전기차 구매보조금
    with col1:
        st.header('전기차 구매보조금')

        # 시도 선택
        시도 = st.selectbox('시도를 선택하세요', ec_gift['시도'].unique(), key='ec_sido')

        # 지역구분 선택
        지역구분 = st.selectbox('지역구분을 선택하세요', ec_gift[ec_gift['시도'] == 시도]['지역구분'].unique(), key='ec_region')

        # 보조금 정보 필터링
        filtered_data_ec = ec_gift[(ec_gift['시도'] == 시도) & (ec_gift['지역구분'] == 지역구분)]

        if len(filtered_data_ec) > 0:
            st.write(filtered_data_ec[['보조금/승용(만원)', '보조금/초소형(만원)']])
        else:
            st.write("선택한 지역의 보조금 정보가 없습니다.")

    # 오른쪽: 차량 목록 및 변경하기 버튼
    with col2:
        st.header('모델을 선택하세요')

        # 필터링된 차량 목록 (연료구분: 전기차, 수소차)
        fuel_filter = st.selectbox('차량 연료구분 선택', ['전기', '수소'], key='fuel_select')
        filtered_car_list = car_list[car_list['연료구분'] == fuel_filter]

        # 모델명 선택 (첫 번째 모델을 기본값으로 설정)
        selected_car = st.selectbox('모델명 선택', filtered_car_list['모델명'].unique(), key='model_select', index=0)

        # 선택된 차량이 데이터에 존재하는지 확인
        if selected_car in filtered_car_list['모델명'].values:
            car_info = filtered_car_list[filtered_car_list['모델명'] == selected_car].iloc[0]
            
            # 이미지 URL을 Base64로 인코딩하여 표시
            encoded_image = encode_image_from_url_to_base64(car_info['img_url'])
            if encoded_image:
                st.markdown(f'<img src="data:image/jpeg;base64,{encoded_image}" alt="Image" width="200">', unsafe_allow_html=True)
            else:
                st.warning("이미지 로드 실패")

            st.write(f"모델명: {car_info['모델명']}")
            st.write(f"연료구분: {car_info['연료구분']}")
            st.write(f"트림명: {car_info['트림명']}")

            # 변경하기 버튼
            if st.button("변경하기"):
                st.session_state.selected_car = car_info
                st.success(f"차량 변경 완료: {car_info['모델명']}")
        else:
            st.warning("선택한 모델은 데이터에 존재하지 않습니다.")