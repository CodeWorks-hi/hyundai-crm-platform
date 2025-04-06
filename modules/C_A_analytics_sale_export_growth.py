# 판매·수출 관리
    # 판매·수출 관리 
        # 해외 판매(수출 관리)수출입 국가별 분석
            # 해외 성장률 트렌드 분석

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
def export_growth_ui():
    # 데이터 로드
    df = load_and_merge_export_data()
    if df is None:
        st.error("❌ 수출 데이터를 불러오지 못했습니다.")
        return

    month_cols = extract_month_columns(df)
    year_list = extract_year_list(df)

    st.subheader("🎯 목표 수출 달성률")
    brand, year, country = get_filter_values(df, "export_4")
    goal = st.number_input(" 수출 목표 (대)", min_value=0, step=10000, value=200000)

    # 1. 연도별 총수출량 컬럼 생성
    all_years = sorted({col[:4] for col in df.columns if "-" in col and col[:4].isdigit()})
    total_export_by_year = {}

    for y in all_years:
        year_cols = [col for col in df.columns if col.startswith(y) and "-" in col]
        yearly_filtered = df[(df["브랜드"] == brand) & (df["지역명"] == country)]
        if year_cols and not yearly_filtered.empty:
            total = yearly_filtered[year_cols].sum(numeric_only=True).sum()
            total_export_by_year[f"{y}-총수출"] = int(total)

    # 2. export_df 생성
    export_df = pd.DataFrame([total_export_by_year])
    export_df.insert(0, "지역명", country)
    export_df.insert(0, "브랜드", brand)

    target_col = f"{year}-총수출"
    actual = int(export_df[target_col].values[0]) if target_col in export_df.columns else 0
    rate = round((actual / goal * 100), 2) if goal > 0 else 0

    # 동적 색상 설정
    if rate < 50:
        bar_color = "#FF6B6B"  # 빨강
        step_colors = ["#FFE8E8", "#FFC9C9", "#FFAAAA"]  # 연한 빨강 계열
    elif rate < 75:
        bar_color = "#FFD93D"  # 주황
        step_colors = ["#FFF3CD", "#FFE69C", "#FFD96B"]  # 연한 주황 계열
    else:
        bar_color = "#6BCB77"  # 초록
        step_colors = ["#E8F5E9", "#C8E6C9", "#A5D6A7"]  # 연한 초록 계열

    # 게이지 차트 생성
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=rate,
        title={'text': f"{year}년 {brand} {country} 목표 달성률"},
        delta={'reference': 100},
        gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': bar_color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 33], 'color': step_colors[0]},
                    {'range': [33, 66], 'color': step_colors[1]},
                    {'range': [66, 100], 'color': step_colors[2]}
                ],
                'threshold': {
                    'line': {'color': "darkred", 'width': 4},
                    'thickness': 0.75,
                    'value': rate
            }
        }
    ))


    fig_gauge.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="white",
        font=dict(color="darkblue", size=16)
    )

    # 차트 출력
    st.plotly_chart(fig_gauge, use_container_width=True)

    # 추가 정보 표시
    st.write("### 추가 정보")
    col1, col2,col3 = st.columns(3)
    col1.info(f"**목표 수출량**\n\n{goal:,} 대")
    col2.info(f"**실제 수출량**\n\n{actual:,} 대")
    col3.info(f"**목표 달성률**\n\n{rate:.2f}%")

    # 원본 데이터 보기
    with st.expander(" 원본 데이터 보기"):
        st.dataframe(df, use_container_width=True)

