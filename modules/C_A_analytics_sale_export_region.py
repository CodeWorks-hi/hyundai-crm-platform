# 판매·수출 관리
    # 판매·수출 관리 
        # 해외 판매(수출 관리)수출입 국가별 분석
            # 해외  시장 비교

import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import urllib3
import re

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

# 데이터 로드 및 처리 함수
def load_and_process_export_data(hyundai_path="data/processed/total/hyundai-by-region.csv"):
    df = load_csv(hyundai_path)
    if df is None:
        return None

    if "차량 구분" not in df.columns:
        df["차량 구분"] = "기타"

    df = extract_year_column(df)
    return df

# 연도 컬럼 추가 함수
def extract_year_column(df):
    month_cols = [col for col in df.columns if re.match(r"\d{4}-\d{2}", col)]
    if "연도" not in df.columns:
        def get_year(row):
            valid_years = [int(col.split("-")[0]) for col in month_cols if pd.notnull(row[col])]
            return max(valid_years) if valid_years else None
        df["연도"] = df.apply(get_year, axis=1)
    df["연도"].fillna('전체', inplace=True)
    return df

# 월별 컬럼 추출
def extract_month_columns(df):
    return [col for col in df.columns if "-" in col and col[:4].isdigit()]

# 연도 추출
def extract_year_list(df):
    return sorted({int(col.split("-")[0]) for col in df.columns if re.match(r"\d{4}-\d{2}", col)})

# 메인 UI 함수
def export_region_ui():
    df = load_and_process_export_data()
    if df is None:
        st.error("❌ 데이터를 불러오지 못했습니다.")
        return

    month_cols = extract_month_columns(df)


    # 연도 선택
    selected_year = st.selectbox(" 연도를 선택하세요", options=extract_year_list(df), index=0)

    # 연도 필터링
    year_cols = [col for col in month_cols if col.startswith(str(selected_year))]

    if not year_cols:
        st.warning("선택된 연도에 데이터가 없습니다.")
        return

    compare_df = df.groupby("지역명")[year_cols].sum().reset_index()
    melted_df = compare_df.melt(id_vars=["지역명"], var_name="월", value_name="수출량")

    fig = px.bar(
        melted_df,
        x="지역명",
        y="수출량",
        color="지역명",
        animation_frame="월",
        title=f"국가별 월별 수출량 비교 ({selected_year})"
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("국가별 수출 성장률 분석")

    col1, col2, col3 = st.columns(3)
    with col1:
        country = st.selectbox(" 국가 선택", options=df["지역명"].unique())
    with col2:
        start_year = st.selectbox("🔻 시작 연도", options=extract_year_list(df), index=0)
    with col3:
        end_year = st.selectbox("🔺 끝 연도", options=extract_year_list(df)[::-1], index=0)

    if start_year >= end_year:
        st.warning("끝 연도가 시작 연도보다 더 커야 합니다.")
        return

    export_by_year = {}
    for year in range(start_year, end_year + 1):
        year_cols = [col for col in month_cols if col.startswith(str(year))]
        filtered = df[df["지역명"] == country]
        if not filtered.empty:
            total_export = filtered[year_cols].sum().sum()
            export_by_year[year] = total_export

    growth_df = pd.DataFrame({
        "연도": list(export_by_year.keys()),
        "총수출": list(export_by_year.values())
    }).sort_values("연도")

    growth_df["전년대비 성장률(%)"] = growth_df["총수출"].pct_change().fillna(0) * 100

    line_chart = alt.Chart(growth_df).mark_line(point=True).encode(
        x='연도:O',
        y='전년대비 성장률(%):Q',
        tooltip=['연도', '총수출', '전년대비 성장률(%)']
    ).properties(
        title=f"{country}의 {start_year}-{end_year} 수출 성장률 변화",
        width=700,
        height=400
    )

    st.altair_chart(line_chart, use_container_width=True)

    # 데이터 확인 및 다운로드
    with st.expander("🗂 원본 데이터 보기"):
        st.dataframe(growth_df)

    csv = growth_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 데이터 다운로드", csv, f"{country}_{start_year}_{end_year}_수출성장률.csv", "text/csv")

