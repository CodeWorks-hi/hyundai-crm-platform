# 판매·수출 관리
    # 판매·수출 관리 
        # 해외 판매(수출 관리)수출입 국가별 분석
            # 해외  시장 비교



import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import urllib3
import re
import ace_tools_open as tools

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
def load_and_merge_export_data(hyundai_path="data/processed/total/hyundai-by-region.csv", 
                                kia_path="data/processed/total/kia-by-region.csv"):
    df_h = load_csv(hyundai_path)
    df_k = load_csv(kia_path)
    
    if df_h is None or df_k is None:
        return None

    df_h["브랜드"] = "현대"
    df_k["브랜드"] = "기아"
    
    if "차량 구분" not in df_h.columns:
        df_h["차량 구분"] = "기타"
    
    # 데이터 병합
    df = pd.concat([df_h, df_k], ignore_index=True)
    
    # '연도' 컬럼 추가
    df = extract_year_column(df)  # 연도 컬럼 추가
    
    
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
def export_region_ui():
    # 데이터 로드
    df = load_and_merge_export_data()
    if df is None:
        st.error("❌ 수출 데이터를 불러오지 못했습니다.")
        return

    month_cols = extract_month_columns(df)
    year_list = extract_year_list(df)

    st.subheader("국가별 비교")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        brand = st.selectbox(
            "브랜드 선택",
            options=df["브랜드"].dropna().unique(),
            key="select_brand"
        )

    if not brand:
        st.warning("브랜드를 선택해야 합니다.")
        return
        
    grouped = df[df["브랜드"] == brand]
        
    if grouped.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        compare_df = grouped.groupby("지역명")[month_cols].sum(numeric_only=True).reset_index()
        melted_df = compare_df.melt(id_vars=["지역명"], var_name="월", value_name="수출량")

        fig = px.bar(
            melted_df,
            x="지역명",
            y="수출량",
            color="지역명",
            animation_frame="월",
            title=f"{brand} 국가별 월별 수출량 비교"
        )
        fig.update_layout(height=600, width=800)
        st.plotly_chart(fig, use_container_width=True)



    st.subheader("📈 국가별 수출 성장률 분석")

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        brand = st.selectbox(
            "브랜드 선택",
            options=df["브랜드"].dropna().unique(),
            key="t5_brand"
        )
        
    with col2:
        year_list = extract_year_list(df)
        start_year = st.selectbox(
            "시작 연도 선택",
            options=year_list,
            key="t5_start_year"
        )
        
    with col3:
        year_list = extract_year_list(df)
        end_year = st.selectbox(
            "끝 연도 선택",
            options=year_list[::-1],  # 역순으로 정렬
            index=1,
            key="t5_end_year"
        )
        
    with col4:
        country_list = df[df["브랜드"] == brand]["지역명"].dropna().unique()
        country = st.selectbox(
            "국가 선택",
            options=country_list if len(country_list) > 0 else ["선택 가능한 국가 없음"],
            key="t5_country"
        )

    # 연도 목록
    year_list = sorted({int(col[:4]) for col in df.columns if "-" in col and col[:4].isdigit()})

    # 연도별 총수출량 계산
    export_by_year = {}
    for y in year_list:
        year_cols = [col for col in df.columns if col.startswith(str(y))]
        filtered = df[(df["브랜드"] == brand) & (df["지역명"] == country)]
        if not filtered.empty:
            total = filtered[year_cols].sum(numeric_only=True).sum()
            export_by_year[y] = total

    # 최소 2개 연도 이상 필요
    if start_year >= end_year:
        st.warning("성장 변화율 분석을 위해 최소 2개 연도의 데이터가 필요합니다.")
    else:
        # 데이터프레임 구성 및 성장률 계산
        growth_df = pd.DataFrame({
            "연도": list(export_by_year.keys()),
            "총수출": list(export_by_year.values())
        }).sort_values("연도")

        growth_df["전년대비 성장률(%)"] = growth_df["총수출"].pct_change().round(4) * 100

        # ✅ 선택된 연도 범위로 필터링 (start_year+1부터)
        filtered_growth_df = growth_df[
            (growth_df["연도"] >= start_year) & (growth_df["연도"] <= end_year)
        ]

        # 차트
        line_chart = alt.Chart(filtered_growth_df).mark_line(point=True).encode(
            x="연도:O",
            y=alt.Y("전년대비 성장률(%):Q", title="성장률 (%)"),
            tooltip=["연도", "전년대비 성장률(%)"]
        ).properties(
            title=f"📊 {start_year}년 ~ {end_year}년 {country} 수출 성장률 변화",
            width=700,
            height=400
        )
        st.altair_chart(line_chart, use_container_width=True)
