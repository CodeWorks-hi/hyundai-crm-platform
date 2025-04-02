import streamlit as st
import requests
import os
from bs4 import BeautifulSoup
import pandas as pd


def fetch_forecast_table():
        url = "https://www.airkorea.or.kr/web/dustForecastWeek?pMENU_NO=193"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        table = soup.find("table", class_="tbl2")
        if not table:
            return pd.DataFrame({"오류": ["표를 찾을 수 없습니다"]})

        rows = table.find_all("tr")
        data = [[cell.get_text(strip=True) for cell in row.find_all(["th", "td"])] for row in rows]
        return pd.DataFrame(data)


def service_ui():
    # 미세먼지 예보 등급 확인
    st.markdown("#### 🌫️ 초미세먼지(PM2.5) 예보 등급 보기")
    st.caption("출처: AirKorea - www.airkorea.or.kr")

    with st.spinner("최신 예보 정보를 불러오는 중..."):
        df = fetch_forecast_table()
        st.dataframe(df, use_container_width=True)

    st.info("이 페이지는 매일 17:30 이후 갱신되는 예보 데이터를 표시합니다.")