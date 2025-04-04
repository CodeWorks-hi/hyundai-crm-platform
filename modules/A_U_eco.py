import pandas as pd
import streamlit as st
import base64
import requests
import streamlit.components.v1 as components
import os
import json
import folium

# 초기 상태값
if "search_query" not in st.session_state:
    st.session_state["search_query"] = ""

# 카카오 API 키 가져오기
def get_api_key():
    key = st.secrets.get('KAKAO_API_KEY', None)
    if key is None:
        key = os.environ.get('KAKAO_API_KEY')
    return key

KAKAO_API_KEY = get_api_key()

DEFAULT_LAT = 37.431095
DEFAULT_LON = 127.128907
DEFAULT_LOCATION = [DEFAULT_LAT, DEFAULT_LON]

char = pd.read_csv("data/char.csv")
char['full_address'] = char['시도'] + " " + char['군구'] + " " + char['주소']


# --------------------------
# 공통 검색 함수
# --------------------------
def search_place(query, keyword):
    query = f"{query} 현대자동차 {keyword}"
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": query, "size": 5}
    response = requests.get(url, headers=headers, params=params)
    return response.json()["documents"] if response.status_code == 200 else []

# --------------------------
# 팝업 HTML 생성 함수
# --------------------------
def create_popup_html(place):
    place_name = place["place_name"]
    address = place["road_address_name"] or place["address_name"]
    phone = place["phone"] or "전화번호 없음"
    detail_url = place["place_url"]
    kakao_map_url = f"https://map.kakao.com/link/from/내위치,{DEFAULT_LAT},{DEFAULT_LON}/to/{place_name},{place['y']},{place['x']}"

    return f"""
    <div style="width:300px;">
        <h4 style="margin-bottom:5px;">{place_name}</h4>
        <p><strong>주소:</strong> {address}</p>
        <p><strong>전화:</strong> {phone}</p>
        <p>
          <a href="{detail_url}" target="_blank" style="color:blue; text-decoration:none;">상세보기</a> |
          <a href="{kakao_map_url}" target="_blank" style="color:blue; text-decoration:none;">길찾기</a>
        </p>
    </div>
    """

# --------------------------
# 메인 함수 (탭 UI 렌더링)
# --------------------------
def render_char_search_map():
# 레이아웃
    col1, col2 = st.columns([1, 5])

    # 🔹 지역 선택
    with col1:
        st.markdown("### 충전소 선택")
        selected_sido = st.selectbox("시도", char['시도'].unique(), key="sido")
        selected_gungu = st.selectbox("군구", char[char['시도'] == selected_sido]['군구'].unique(), key="gungu")

        # 선택된 지역 필터링
        selected_area = char[
            (char['시도'] == selected_sido) &
            (char['군구'] == selected_gungu)
        ].reset_index(drop=True)

        # 충전소 선택
        selected_station = st.selectbox("충전소 선택", selected_area['충전소명'].unique(), key="station")
     
        st.markdown("### 상세 정보")
        selected_info = selected_area[selected_area['충전소명'] == selected_station].iloc[0]
        st.markdown(f"""
        <div style="border:1px solid #ccc; border-radius:10px; padding:12px;">
            <h4>{selected_info['충전소명']}</h4>
            <p><b>주소</b>: {selected_info['주소']}</p>
            <p><b>충전기타입</b>: {selected_info['충전기타입']}</p>
            <p><b>시설구분</b>: {selected_info['시설구분(대)']} / {selected_info['시설구분(소)']}</p>
        </div>
        """, unsafe_allow_html=True)

    # 🔹 지도 표시
    with col2:
        if not selected_area.empty:
            selected_info = selected_area[selected_area['충전소명'] == selected_station].iloc[0]
            full_address = selected_info['주소']
            search_url = "https://dapi.kakao.com/v2/local/search/address.json"
            headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
            params = {"query": full_address}
            res = requests.get(search_url, headers=headers, params=params)
            lat, lon = DEFAULT_LAT, DEFAULT_LON
            if res.status_code == 200 and res.json()["documents"]:
                loc = res.json()["documents"][0]
                lat = float(loc["y"])
                lon = float(loc["x"])
            m = folium.Map(location=[lat, lon], zoom_start=16)
            # 팝업 구성
            popup_html = f"""
            <b>{selected_info['충전소명']}</b><br>
            주소: {selected_info['주소']}<br>
            충전기 타입: {selected_info['충전기타입']}<br>
            시설 구분: {selected_info['시설구분(대)']} / {selected_info['시설구분(소)']}
            """

            folium.Marker(
                [lat, lon],
                tooltip=selected_info['충전소명'],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)
            st.components.v1.html(m._repr_html_(), height=600)

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
    if 'eco_car_page' not in st.session_state:
        st.session_state.eco_car_page = 0
    # 데이터 로드
    suso_gift = pd.read_csv('data/suso_gift.csv')
    ec_gift = pd.read_csv('data/ec_gift.csv')
    char = pd.read_csv('data/char.csv')
    car_list = pd.read_csv('data/hyundae_car_list.csv')

    # 컬럼 col1 (지역 + 모델 선택), col3 (모델 카드)
    col1, a1 ,col2, a2,  col3 = st.columns([1.5, 0.1, 1.5, 0.1, 2])

    with col1:
        st.subheader("구매 지역을 선택하세요.")
        st.caption("2025년 전기차, 수소차 구매보조금을 조회해보세요.")
        selected_sido = st.selectbox("시/도", ec_gift['시도'].unique())
        selected_sigungu = st.selectbox("시/군/구", ec_gift[ec_gift['시도'] == selected_sido]['지역구분'].unique())

        # 연료구분 고정 전기차
        selected_fuel = '전기'
        filtered_models = car_list[car_list['연료구분'] == selected_fuel]['모델명'].unique()
        selected_modelname = st.selectbox("전기차 모델 선택", filtered_models)
        st.session_state.selected_modelname = selected_modelname

        st.success("전기차 보조금 지급 현황")

        elec_data = ec_gift[
            (ec_gift['시도'] == selected_sido) &
            (ec_gift['지역구분'] == selected_sigungu)
        ]
        if not elec_data.empty:
            col_a, col_b = st.columns(2)
            with col_a:
                with st.container():
                    st.markdown(f"<div style='padding: 10px; border-radius: 8px; text-align: center;'><h3 style='margin:0;'> 승용 </h3></div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='padding: 10px; background-color: #f5f5f5; border-radius: 8px; text-align: center;'><h4 style='margin:0;'>{elec_data.iloc[0]['보조금/승용(만원)']}만원</h4></div>", unsafe_allow_html=True)
            with col_b:
                with st.container():
                    st.markdown(f"<div style='padding: 10px; border-radius: 8px; text-align: center;'><h3 style='margin:0;'> 초소형</h3></div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='padding: 10px; background-color: #f5f5f5; border-radius: 8px; text-align: center;'><h4 style='margin:0;'>{elec_data.iloc[0]['보조금/초소형(만원)']}만원</h4></div>", unsafe_allow_html=True)
        else:
            st.info("보조금 데이터가 없습니다.")

    with col2:
        st.subheader("모델을 선택하세요")
        eco_cars = car_list[
            (car_list['연료구분'] == '전기') &
            (car_list['모델명'] == st.session_state.selected_modelname)
        ].reset_index(drop=True)

        page_size = 3
        total_pages = (len(eco_cars) - 1) // page_size + 1
        if 'eco_car_page' not in st.session_state:
            st.session_state.eco_car_page = 0

        start_idx = st.session_state.eco_car_page * page_size
        end_idx = start_idx + page_size
        current_page_cars = eco_cars.iloc[start_idx:end_idx]

        with st.expander("모델별 트림 보기", expanded=True):
            for idx, row in current_page_cars.iterrows():
                st.markdown("---")
                col_img, col_txt = st.columns([1, 3])
                with col_img:
                    img64 = encode_image_from_url_to_base64(row['img_url'])
                    if img64:
                        st.markdown(f'<img src="data:image/jpeg;base64,{img64}" width="120">', unsafe_allow_html=True)
                with col_txt:
                    st.markdown(f"**{row['모델명']}**")
                    st.caption(f"{row['트림명']} / {row['연료구분']}")
                    if st.button(f"{row['모델명']} {row['트림명']} 선택", key=f"{row['모델명']}_{row['트림명']}_{idx}"):
                        st.session_state.selected_model = row['모델명']
                        st.session_state.selected_trim = row['트림명']
                        st.rerun()

            nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
            with nav_col1:
                if st.session_state.eco_car_page > 0:
                    if st.button("⬅ 이전 페이지"):
                        st.session_state.eco_car_page -= 1
                        st.rerun()
            with nav_col2:
                st.markdown(f"페이지 {st.session_state.eco_car_page + 1} / {total_pages}")
            with nav_col3:
                if st.session_state.eco_car_page < total_pages - 1:
                    if st.button("다음 페이지 ➡"):
                        st.session_state.eco_car_page += 1
                        st.rerun()
    with col3:
        st.markdown("### 조회 결과")
        # 선택된 모델 이미지 및 기본 정보 표시
        if 'selected_model' in st.session_state:
            result_info = car_list[
                (car_list['모델명'] == st.session_state.selected_model) &
                (car_list['트림명'] == st.session_state.selected_trim)
            ].iloc[0]

            # 차량 가격
            price = result_info['기본가격']
            
            # 차량구분 기반 보조금 타입
            support_type = "초소형 보조금" if result_info['차량구분'] == '소형' else "승용 보조금"

            # 예시 보조금 (향후 실제 값 연동 예정)
            subsidy = 4000000 if support_type == "승용 보조금" else 7000000
            final_price = price - subsidy

            # 카드 형태 정보 출력
            
            st.markdown(f"""
                <div style="border:1px solid #ccc; border-radius:10px; padding:16px; margin-bottom:16px;">
                    <h4 style="margin-bottom:0;">{result_info['모델명']}</h4>
                    <p style="margin-top:4px; color:gray;">{result_info['트림명']}</p>
                    <p><b>차량 가격 (세제혜택 후):</b> {price:,} 원</p>
                    <p><b>보조금 유형:</b> {support_type}</p>
                    <p><b>금 액 :</b> {subsidy:,} 원</p>
                    <p><b>지자체 보조금:</b> 표시 예정</p>
                    <p><b>최종금액:</b> {price:,} 원 - {subsidy:,} 원 = <b>{final_price:,} 원</b></p>
                </div>
            """, unsafe_allow_html=True)

            # 이미지 아래 출력
            encoded = encode_image_from_url_to_base64(result_info['img_url'])
            if encoded:
                st.markdown(f'<img src="data:image/jpeg;base64,{encoded}" width="100%" style="margin-top:10px;">', unsafe_allow_html=True)
    st.markdown("---")
    render_char_search_map()
