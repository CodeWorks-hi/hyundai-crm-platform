import streamlit as st
import requests
import os

def get_api_key():
    return st.secrets["AIR_QUALITY_API_KEY"]

def get_station_list(addr: str, service_key: str):
    url = "http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getMsrstnList"
    params = {
        "addr": addr,
        "returnType": "json",
        "serviceKey": service_key
    }

    response = requests.get(url, params=params)
    st.write(f"[상태 코드] {response.status_code}")
    st.write(f"[응답 본문] {response.text[:300]}")

    try:
        return [item["stationName"] for item in response.json()["response"]["body"]["items"]]
    except Exception as e:
        raise Exception(f"❌ JSON 파싱 실패!\n{e}\n본문:\n{response.text}")

def get_air_quality_by_station(station_name: str, service_key: str):
    url = "http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"
    params = {
        "stationName": station_name,       # 테스트용 측정소
        "dataTerm": "DAILY",
        "pageNo": 1,
        "numOfRows": 100,
        "returnType": "json",         # 꼭 소문자, 정확하게
        "serviceKey": service_key,
        "ver": "1.0"
    }

    headers = {
        "Accept": "application/json"
    }

    response = requests.get(url, params=params, headers=headers)

    # 확인
    print("응답 타입:", response.headers.get("Content-Type"))
    print("본문:", response.text[:300])

def eco_ui():
    service_key = get_api_key()

    region = st.text_input("측정 지역 입력 (예: 서울)")

    if st.button("대기질 정보 확인하기") and region:
        stations = get_station_list(region, service_key)
        st.write(f"📍 '{region}' 지역의 측정소 목록:", stations)

        if stations:
            st.write(f"📡 '{stations[0]}'의 대기질 측정값:")
            air_data = get_air_quality_by_station(stations[0], service_key)

            items = air_data["response"]["body"]["items"]
            if items:
                st.json(items[0])
            else:
                st.warning("❗ 측정값이 존재하지 않습니다.")
        else:
            st.warning("❗ 해당 지역에는 등록된 측정소가 없습니다.")

