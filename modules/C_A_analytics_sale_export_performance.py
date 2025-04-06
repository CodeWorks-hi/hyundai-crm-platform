# 판매·수출 관리
    # 판매·수출 관리 
        # 해외 판매(수출 관리)수출입 국가별 분석
            # 해외 실적 분석

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

    # 브랜드 컬럼 추가
    if "브랜드" not in df.columns:
        df["브랜드"] = "현대"

    # 차량 구분 컬럼 추가
    if "차량 구분" not in df.columns:
        df["차량 구분"] = "기타"

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
    col1, col2, col3 = st.columns(3)
    
    with col1:
        brand = st.selectbox(
            "브랜드 선택",
            options=df["브랜드"].dropna().unique(),
            key=f"{key_prefix}_brand"
        )
    
    with col2:
        year_list = extract_year_list(df)
        year = st.selectbox(
            "연도 선택",
            options=year_list[::-1],  # 역순으로 정렬
            index=1,
            key=f"{key_prefix}_year"
        )
    
    with col3:
        country_list = df[df["브랜드"] == brand]["지역명"].dropna().unique()
        country = st.selectbox(
            "국가 선택",
            options=country_list if len(country_list) > 0 else ["선택 가능한 국가 없음"],
            key=f"{key_prefix}_country"
        )
    
    return brand, year, country

# 수출 UI ======================== 메인화면 시작 함수 
def export_performance_ui():
    # 데이터 로드
    df = load_and_merge_export_data()
    if df is None:
        st.error("❌ 수출 데이터를 불러오지 못했습니다.")
        return

    month_cols = extract_month_columns(df)
    year_list = extract_year_list(df)


    # 월 컬럼 추출
    month_cols = extract_month_columns(df)

    # 필터링 UI 호출
    brand, year, country = get_filter_values(df, "export_1")

    if not year:  # 만약 'year'가 선택되지 않았다면 경고 메시지 출력
        st.warning("연도를 선택해야 합니다.")
        return
        
    # 월 필터링 컬럼
    month_filter_cols = [col for col in month_cols if col.startswith(str(year))]
    filtered = df[(df["브랜드"] == brand) & (df["지역명"] == country)]

    if not filtered.empty:
        total_export = int(filtered[month_filter_cols].sum(numeric_only=True).sum(skipna=True))
        avg_export = int(filtered[month_filter_cols].mean(numeric_only=True).mean(skipna=True))
        type_count = filtered["차량 구분"].nunique()

        # 월별 수출량 차트
        df_melted = filtered.melt(id_vars=["차량 구분"], value_vars=month_filter_cols, var_name="월", value_name="수출량")
        df_melted.dropna(subset=["수출량"], inplace=True)
        df_melted["월_숫자"] = df_melted["월"].apply(lambda x: int(x.split("-")[1]))

        if not df_melted.empty:
            # 라인차트
            fig_line = px.line(
                df_melted,
                x="월",
                y="수출량",
                color="차량 구분",
                markers=True,
                line_shape="spline",
                title="차량 구분별 수출량 변화 추이 (라인차트)"
            )
            fig_line.update_layout(
                xaxis_title="월",
                yaxis_title="수출량",
                height=400,
                template="plotly_white"
            )

            # 📊 바차트
            fig_bar = px.bar(
                df_melted,
                x="월",
                y="수출량",
                color="차량 구분",
                barmode="group",
                title="차량 구분별 수출량 변화 추이 (막대차트)"
            )
            fig_bar.update_layout(
                xaxis_title="월",
                yaxis_title="수출량",
                height=400,
                template="plotly_white"
            )
            col1, col2 = st.columns([1,1])
            with col1:
                st.plotly_chart(fig_line, use_container_width=True)
            with col2:
                st.plotly_chart(fig_bar, use_container_width=True)
        # 추가 정보 표시
        st.info(f"{year}년 {brand} {country} 수출 실적 ")
        col1, col2, col3= st.columns(3)
        col1.info(f"총 수출량: {total_export:,} 대")
        col2.info(f"평균 수출량: {avg_export:,} 대")
        col3.info(f"차량 구분 수: {type_count} 종")

        st.markdown("---")
        
        # 원본 데이터 보기
        with st.expander(" 원본 데이터 보기"):
            st.dataframe(filtered, use_container_width=True)

        # CSV 다운로드
        csv = filtered.to_csv(index=False).encode("utf-8-sig")
        st.download_button("현재 데이터 다운로드", data=csv, file_name=f"{brand}_{country}_{year}_수출실적.csv", mime="text/csv")
    else:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")

