import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib3
import re

# SSL 경고 메시지 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 데이터 로드 함수
@st.cache_data
def load_csv(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"csv 파일 로드 중 오류 발생: {str(e)}")
        return None

# 데이터 병합 및 연도 컬럼 추가
@st.cache_data
def load_and_prepare_export_data(path="data/processed/total/hyundai-by-region.csv"):
    df = load_csv(path)
    if df is None:
        return None

    if "차량 구분" not in df.columns:
        df["차량 구분"] = "기타"

    df = extract_year_column(df)
    return df

# 월 컬럼 추출 함수
def extract_month_columns(df):
    return [col for col in df.columns if re.match(r"\d{4}-\d{2}", col)]

# 연도 리스트 추출 함수
def extract_year_list(df):
    return sorted({int(col.split("-")[0]) for col in df.columns if re.match(r"\d{4}-\d{2}", col)})

# 연도 컬럼 추가 함수
def extract_year_column(df):
    month_cols = extract_month_columns(df)

    if "연도" not in df.columns:
        df["연도"] = df.apply(lambda row: max([int(col[:4]) for col in month_cols if pd.notnull(row[col])]), axis=1)

    df["연도"].fillna('전체', inplace=True)
    return df

# 필터링 UI 생성 함수
def get_filter_values(df, key_prefix):
    col1, col2 = st.columns(2)

    with col1:
        year_list = extract_year_list(df)
        year = st.selectbox("연도 선택", options=year_list[::-1], index=1, key=f"{key_prefix}_year")

    with col2:
        country_list = df["지역명"].dropna().unique()
        country = st.selectbox("국가 선택", options=country_list, key=f"{key_prefix}_country")

    return year, country

# 메인 UI 함수
def export_performance_ui():
    df = load_and_prepare_export_data()
    if df is None:
        st.error("❌ 수출 데이터를 불러오지 못했습니다.")
        return

    month_cols = extract_month_columns(df)
    year, country = get_filter_values(df, "export")

    month_filter_cols = [col for col in month_cols if col.startswith(str(year))]
    filtered = df[df["지역명"] == country]

    if not filtered.empty:
        total_export = int(filtered[month_filter_cols].sum().sum())
        avg_export = int(filtered[month_filter_cols].mean().mean())
        type_count = filtered["차량 구분"].nunique()

        df_melted = filtered.melt(id_vars=["차량 구분"], value_vars=month_filter_cols, var_name="월", value_name="수출량")
        df_melted.dropna(subset=["수출량"], inplace=True)

        if not df_melted.empty:
            fig_line = px.line(
                df_melted,
                x="월",
                y="수출량",
                color="차량 구분",
                markers=True,
                line_shape="spline",
                title=f"{year}년 {country} 차량 구분별 수출량 변화 (라인차트)"
            )

            fig_bar = px.bar(
                df_melted,
                x="월",
                y="수출량",
                color="차량 구분",
                barmode="group",
                title=f"{year}년 {country} 차량 구분별 수출량 변화 (막대차트)"
            )

            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(fig_line, use_container_width=True)
            with col2:
                st.plotly_chart(fig_bar, use_container_width=True)

        st.info(f"📌 {year}년 {country} 수출 실적 요약")
        col1, col2, col3 = st.columns(3)
        col1.metric("총 수출량", f"{total_export:,} 대")
        col2.metric("평균 월 수출량", f"{avg_export:,} 대")
        col3.metric("차량 구분 수", f"{type_count} 종")

        with st.expander("🔍 원본 데이터 보기"):
            st.dataframe(filtered, use_container_width=True)

        csv = filtered.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 데이터 다운로드", data=csv, file_name=f"{country}_{year}_수출실적.csv", mime="text/csv")
    else:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
