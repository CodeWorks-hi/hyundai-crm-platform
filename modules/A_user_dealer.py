# 고객 메인 대시보드   
# 대리점 및 정비소 지도화
# 대리점 및 정비소 리스트


import streamlit as st
import requests
import folium
import os
import streamlit.components.v1 as components
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb

if "search_query" not in st.session_state:
    st.session_state["search_query"] = ""

def get_api_key():
    key = os.environ.get('KAKAO_API_KEY')
    if key is None:
        key = st.secrets.get('KAKAO_API_KEY')
    return key

KAKAO_API_KEY = get_api_key()

DEFAULT_LAT = 37.431095
DEFAULT_LON = 127.128907

# 1) 지점/대리점 검색 함수
def search_dealership(query, x=None, y=None):
    query = query + " 현대자동차 지점"
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": query, "size": 4}
    if x and y:
        params["x"] = x
        params["y"] = y
        params["radius"] = 10000
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["documents"]
    else:
        return []
    
# 2) 정비소 검색 함수
def search_repairshop(query, x=None, y=None):
    query = query + " 현대자동차 정비소"
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": query, "size": 4}
    if x and y:
        params["x"] = x
        params["y"] = y
        params["radius"] = 10000
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["documents"]
    else:
        return []

# 3) 상세 정보 팝업 HTML 생성 함수
def create_popup_html(place):
    place_name = place["place_name"]
    address = place["road_address_name"] if place["road_address_name"] else place["address_name"]
    phone = place["phone"] if place["phone"] else "전화번호 없음"
    detail_url = place["place_url"]
    kakao_map_url = f"https://map.kakao.com/link/from/내위치,{DEFAULT_LAT},{DEFAULT_LON}/to/{place_name},{place['y']},{place['x']}"
    
    popup_html = f"""
    <div style="width:300px;">
        <h4 style="margin-bottom:5px;">🔹 {place_name}</h4>
        <p><strong>📍 주소:</strong> {address}</p>
        <p><strong>📞 전화:</strong> {phone}</p>
        <p>
          <a href="{detail_url}" target="_blank" style="color:blue; text-decoration:none; font-weight:bold;">
            📷 상세보기
          </a>
          &nbsp;|&nbsp;
          <a href="{kakao_map_url}" target="_blank" style="color:blue; text-decoration:none; font-weight:bold;">
            🗺️ 길찾기
          </a>
        </p>
    </div>
    """
    return popup_html

# ------------------------------
# 4) Streamlit UI
# ------------------------------

search_query = ''

st.title("매장 찾기")

tab1, tab2 = st.tabs(['지점 찾기', '정비소 찾기'])
with tab1:
    st.write("## 🔍 지점 찾기")

    # 모란 지역 (디폴트 지도 중심)
    DEFAULT_LOCATION = [37.41114, 127.12952]

    # 좌(지도 + 검색어) : 우(결과 리스트) = 2 : 1 비율
    col_map, col_list = st.columns([2, 1])

    with col_map:
        search_query = st.text_input("검색어를 입력하세요 :", key="dealership_input", value=st.session_state['search_query'])

        if not search_query:
            m = folium.Map(location=DEFAULT_LOCATION, zoom_start=13)
        else:
            results = search_dealership(search_query)
            if results:
                first_place = results[0]
                map_center = [float(first_place["y"]), float(first_place["x"])]
                m = folium.Map(location=map_center, zoom_start=13)

                for i, place in enumerate(results, start=1):
                    folium.Marker(
                        location=[float(place["y"]), float(place["x"])],
                        popup=folium.Popup(create_popup_html(place), max_width=300),
                        tooltip=f"{i}. {place['place_name']}",
                        icon=folium.Icon(color="blue", icon="info-sign")
                    ).add_to(m)

        # 지도 HTML 저장 및 렌더링
        map_html = m._repr_html_()
        components.html(
            f"""
            <div style="width:1000px; height:500px;">
                {map_html}
            </div>
            """,
            height=800,
        )

    with col_list:
        st.write("")
        if search_query:
            results = search_dealership(search_query)
            if results:
                st.write(f"**검색 결과 ({len(results)}개)**")
                for i, place in enumerate(results, start=1):
                    # 프레이스 네임을 클릭하면 상세 페이지로 이동하도록 마크다운 링크 생성
                    st.markdown(f"**{i}. [{place['place_name']}]({place['place_url']})**", unsafe_allow_html=True)
                    st.caption(f"{place['road_address_name'] or place['address_name']}")
                    if place["phone"]:
                        st.caption(f"📞 {place['phone']}")
                    st.write("---")
        else:
            st.info("아직 검색어가 없습니다.")
            
with tab2:
    st.write("## 🔍 정비소 찾기")

    # 모란 지역 (디폴트 지도 중심)
    DEFAULT_LOCATION = [37.41114, 127.12952]

    # 좌(지도 + 검색어) : 우(결과 리스트) = 2 : 1 비율
    col_map, col_list = st.columns([2, 1])

    with col_map:
        search_query = st.text_input("검색어를 입력하세요 :", key="repairshop_input", value=st.session_state['search_query'])

        if not search_query:
            m = folium.Map(location=DEFAULT_LOCATION, zoom_start=13)
        else:
            results = search_repairshop(search_query)
            if results:
                first_place = results[0]
                map_center = [float(first_place["y"]), float(first_place["x"])]
                m = folium.Map(location=map_center, zoom_start=13)

                for i, place in enumerate(results, start=1):
                    folium.Marker(
                        location=[float(place["y"]), float(place["x"])],
                        popup=folium.Popup(create_popup_html(place), max_width=300),
                        tooltip=f"{i}. {place['place_name']}",
                        icon=folium.Icon(color="blue", icon="info-sign")
                    ).add_to(m)

        # 지도 HTML 저장 및 렌더링
        map_html = m._repr_html_()
        components.html(
            f"""
            <div style="width:1000px; height:500px;">
                {map_html}
            </div>
            """,
            height=800,
        )

    with col_list:
        st.write("")
        if search_query:
            results = search_repairshop(search_query)
            if results:
                st.write(f"**검색 결과 ({len(results)}개)**")
                for i, place in enumerate(results, start=1):
                    # 프레이스 네임을 클릭하면 상세 페이지로 이동하도록 마크다운 링크 생성
                    st.markdown(f"**{i}. [{place['place_name']}]({place['place_url']})**", unsafe_allow_html=True)
                    st.caption(f"{place['road_address_name'] or place['address_name']}")
                    if place["phone"]:
                        st.caption(f"📞 {place['phone']}")
                    st.write("---")
        else:
            st.info("아직 검색어가 없습니다.")
