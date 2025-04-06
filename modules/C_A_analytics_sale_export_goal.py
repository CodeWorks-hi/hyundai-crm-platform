# 판매·수출 관리
    # 판매·수출 관리 
        # 해외 판매(수출 관리)수출입 국가별 분석
            # 해외 목표 달성률 집계

import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import urllib3
import re


# 수출관리 

# SSL 경고 메시지 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 데이터 로드 함수 - 캐시 처리
@st.cache_data
def load_csv(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"csv 파일 로드 중 오류 발생: {str(e)}")
        return None

# 데이터 병합 함수 (수출 실적)
def load_and_merge_export_data(hyundai_path="data/processed/total/hyundai-by-region.csv"):
    # 현대 데이터 로드
    df = load_csv(hyundai_path)
    
    # 데이터 로드 실패 시 조기 반환
    if df is None:
        return None

    # 연도 컬럼 추가
    df = extract_year_column(df)
    
    return df

# 월별 컬럼 추출 함수
def extract_month_columns(df):
    return [col for col in df.columns if "-" in col and col[:4].isdigit()]

# 연도 리스트 추출 함수
def extract_year_list(df):
    return sorted({
        int(col.split("-")[0])
        for col in df.columns
        if re.match(r"\d{4}-\d{2}", col)
    })

# 월 리스트 추출 함수 (특정 연도에 대해)
def extract_month_list(df, year: int):
    return sorted({
        int(col.split("-")[1])
        for col in df.columns
        if col.startswith(str(year)) and re.match(r"\d{4}-\d{2}", col)
    })

# 연도 컬럼 추가 함수
def extract_year_column(df):
    # 월별 컬럼을 가져오는 함수
    month_cols = extract_month_columns(df)
    
    # '연도' 컬럼이 없으면 추가
    if "연도" not in df.columns:
        def get_year(row):
            # 유효한 월별 컬럼을 통해 연도 추출
            valid_years = [int(col.split("-")[0]) for col in month_cols if pd.notnull(row[col])]
            return max(valid_years) if valid_years else None
        
        # '연도' 컬럼 추가
        df["연도"] = df.apply(get_year, axis=1)
    
    # NaN 값이 있는 '연도' 컬럼을 '전체'로 대체 (필요한 경우)
    df["연도"].fillna('전체', inplace=True)

    return df

# 필터링 UI 생성 함수
def get_filter_values(df, key_prefix):
    col1, col2= st.columns(2)  # 2열로 변경
    
    with col1:
        year_list = extract_year_list(df)
        year = st.selectbox(
            "연도 선택",
            options=year_list[::-1],
            index=1,
            key=f"{key_prefix}_year"
        )
    
    with col2:
        country_list = df["지역명"].dropna().unique()
        country = st.selectbox(
            "국가 선택",
            options=country_list if len(country_list) > 0 else ["선택 가능한 국가 없음"],
            key=f"{key_prefix}_country"
        )
    
    return year, country  # 브랜드 제외

# 수출 UI ======================== 메인화면 시작 함수 
def export_goal_ui():
    # 데이터 로드
    df = load_and_merge_export_data()
    if df is None:
        st.error("❌ 수출 데이터를 불러오지 못했습니다.")
        return

    month_cols = extract_month_columns(df)
    year_list = extract_year_list(df)

    col1, col2, col3 = st.columns(3)  # 3열로 변경
        
    with col1:
        start_year = st.selectbox(
            "시작 연도 선택",
            options=year_list,
            key="t3_start_year"
        )
        
    with col2:
        end_year = st.selectbox(
            "끝 연도 선택",
            options=year_list[::-1],
            index=1,
            key="t3_end_year"
        )
        
    with col3:
        country = st.selectbox(
            "국가 선택",
            options=df["지역명"].dropna().unique(),
            key="t3_country"
        )

    if start_year >= end_year :
        st.error("시작 연도는 끝 연도보다 작아야 합니다.")
    else:
        yearly = df[df["지역명"] == country]  # 브랜드 필터 제거

        # 연도 추출
        all_years = sorted({col[:4] for col in df.columns if "-" in col and col[:4].isdigit()})

        # 연도별 총수출량 컬럼 생성
        total_export_by_year = {}

        for y in all_years:
            year_cols = [col for col in df.columns if col.startswith(y) and "-" in col]
            if year_cols:
                total = yearly[year_cols].sum(numeric_only=True).sum()
                total_export_by_year[f"{y}-총수출"] = [int(total)]

        # 데이터프레임으로 변환
        export_df = pd.DataFrame(total_export_by_year)
        export_df.insert(0, "지역명", country)  # 브랜드 컬럼 제거

        # 1. 연도별 총수출 컬럼만 추출
        year_columns = [
            col for col in export_df.columns
            if (
                col.endswith("-총수출")
                and col[:4].isdigit()
                and int(col[:4]) >= start_year
                and int(col[:4]) <= end_year
            )
        ]

        # 2. melt (wide → long)
        line_df = export_df.melt(
            id_vars=["지역명"],  # 브랜드 제외
            value_vars=year_columns,
            var_name="연도", 
            value_name="총수출"
        )

        # 3. '연도' 컬럼에서 '2016-총수출' → '2016' 형태로 정리
        line_df["연도"] = line_df["연도"].str.extract(r"(\d{4})").astype(str)

        # 4. 그래프 그리기
        line_chart = alt.Chart(line_df).mark_line(point=True).encode(
            x=alt.X("연도:O", title="연도"),
            y=alt.Y("총수출:Q", title="총수출"),
            tooltip=["연도", "총수출"]
        ).properties(
            title=f"{country} 연도별 총 수출량 추이",  # 제목에서 브랜드 제거
            width=700,
            height=400
        )

        st.altair_chart(line_chart, use_container_width=True)
