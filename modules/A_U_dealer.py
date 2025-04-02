# 고객 메인 대시보드   
# 대리점 및 정비소 지도화
# 대리점 및 정비소 리스트

import streamlit as st
import requests
import folium
import os
import streamlit.components.v1 as components

# 초기 상태값
if "search_query" not in st.session_state:
    st.session_state["search_query"] = ""

# 카카오 API 키 가져오기
def get_api_key():
    key = os.environ.get('KAKAO_API_KEY')
    if key is None:
        key = st.secrets.get('KAKAO_API_KEY')
    return key

KAKAO_API_KEY = get_api_key()

DEFAULT_LAT = 37.431095
DEFAULT_LON = 127.128907
DEFAULT_LOCATION = [DEFAULT_LAT, DEFAULT_LON]

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
        <h4 style="margin-bottom:5px;">🔹 {place_name}</h4>
        <p><strong>📍 주소:</strong> {address}</p>
        <p><strong>📞 전화:</strong> {phone}</p>
        <p>
          <a href="{detail_url}" target="_blank" style="color:blue; text-decoration:none;">📷 상세보기</a> |
          <a href="{kakao_map_url}" target="_blank" style="color:blue; text-decoration:none;">🗺️ 길찾기</a>
        </p>
    </div>
    """

# --------------------------
# 메인 함수 (탭 UI 렌더링)
# --------------------------
def dealer_ui():
    st.title(" 대리점 및 정비소 찾기")

    tab1, tab2 = st.tabs([' 지점 찾기', ' 정비소 찾기'])

    for tab, keyword in zip([tab1, tab2], ["지점", "정비소"]):
        with tab:
            st.markdown(f"### 🔍 {keyword} 검색")

            col_map, col_list = st.columns([2, 1])

            with col_map:
                search_query = st.text_input(f"{keyword} 검색어 입력:", key=f"{keyword}_input")

                if not search_query:
                    m = folium.Map(location=DEFAULT_LOCATION, zoom_start=13)
                else:
                    results = search_place(search_query, keyword)
                    if results:
                        map_center = [float(results[0]["y"]), float(results[0]["x"])]
                        m = folium.Map(location=map_center, zoom_start=13)
                        for i, place in enumerate(results, start=1):
                            folium.Marker(
                                location=[float(place["y"]), float(place["x"])],
                                popup=folium.Popup(create_popup_html(place), max_width=300),
                                tooltip=f"{i}. {place['place_name']}",
                                icon=folium.Icon(color="blue", icon="info-sign")
                            ).add_to(m)
                    else:
                        m = folium.Map(location=DEFAULT_LOCATION, zoom_start=13)

                components.html(
                    f"""<div style="width:1000px; height:500px;">{m._repr_html_()}</div>""",
                    height=800,
                )

            with col_list:
                st.write("")
                if search_query:
                    results = search_place(search_query, keyword)
                    if results:
                        st.write(f"**검색 결과 ({len(results)}개)**")
                        for i, place in enumerate(results, start=1):
                            st.markdown(f"**{i}. [{place['place_name']}]({place['place_url']})**", unsafe_allow_html=True)
                            st.caption(f"{place['road_address_name'] or place['address_name']}")
                            if place["phone"]:
                                st.caption(f"📞 {place['phone']}")
                            st.write("---")
                    else:
                        st.warning("검색 결과가 없습니다.")
                else:
                    st.info("검색어를 입력해주세요.")

