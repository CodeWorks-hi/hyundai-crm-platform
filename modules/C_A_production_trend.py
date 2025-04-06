# 생산·제조 현황 분석
    # 연도별 추이, 목표 달성률



import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 데이터 불러오기
@st.cache_data
def load_data():
    car_list_path = "data/hyundae_car_list.csv"
    inventory_path = "data/inventory_data.csv"
    hyundai_plant_path = "data/processed/total/hyundai-by-plant.csv"

    df_list = pd.read_csv(car_list_path)
    df_inv = pd.read_csv(inventory_path)
    df_plant = pd.read_csv(hyundai_plant_path)

    # 컬럼 정제 함수 수정
    def clean_df(df):
        df.columns = df.columns.str.strip()
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        return df

    df_list = clean_df(df_list)
    df_inv = clean_df(df_inv)
    df_plant = clean_df(df_plant)

    df_plant['생산상태'] = df_plant['생산상태'].fillna('미확인')

    return df_list, df_inv, df_plant

def trend_ui():
    df_list, df_inv, df_plant = load_data()

    # 생산일 및 연도 컬럼 생성
    df_inv['생산일'] = pd.date_range(start='2022-01-01', periods=len(df_inv), freq='D')
    df_inv['연도'] = df_inv['생산일'].dt.year

    # 분석 리포트 생성
    with st.spinner("데이터 분석 중..."):
        prod_capacity = df_inv.groupby(['공장명', '모델명', '트림명'])['재고량'].min()
        total_prod = prod_capacity.groupby('공장명').sum().reset_index(name='생산가능수량')

        inventory_analysis = df_inv.groupby('공장명').agg(
            총재고량=('재고량', 'sum'),
            평균재고=('재고량', 'mean'),
            고유부품수=('부품명', 'nunique')
        ).reset_index()

        report = pd.merge(total_prod, inventory_analysis, on='공장명')
        report['생산효율'] = (report['생산가능수량'] / report['총재고량'] * 100).round(2)
        report = report.astype({
            '생산가능수량': 'int',
            '총재고량': 'int',
            '고유부품수': 'int'
        })

        st.subheader("현대자동차 생산 현황 실시간 모니터링 시스템")

        cols = st.columns(5)
        st.markdown("""<style>.stMetric {padding: 20px; background-color: #f8f9fa; border-radius: 10px;}</style>""", unsafe_allow_html=True)

        cols[0].metric("최다 재고", f"{report['총재고량'].max():,}개", report.loc[report['총재고량'].idxmax(), '공장명'])
        cols[1].metric("신규 부품", f"{report['고유부품수'].sum():,}종", "2025년 4월 기준")
        cols[2].metric("최대 생산 가능", f"{int(report['생산가능수량'].max()):,}대", report.loc[report['생산가능수량'].idxmax(), '공장명'])
        cols[3].metric("최고 생산 효율", f"{float(report['생산효율'].max()):.2f}%", report.loc[report['생산효율'].idxmax(), '공장명'])
        cols[4].metric("평균 회전율", f"{float(report['생산효율'].mean()):.1f}%", help="전체 공장의 평균 재고 회전율")

    st.markdown("---")

    st.subheader(" 현재 생산 중인 주요 차량 현황")
    current_models = pd.DataFrame({
        '모델명': ['IONIQ5(Long Range)', 'IONIQ6', 'Creta(SU2i LWB)', 'Venue(QXi)', 'Exter(AI3 SUV)'],
        '공장명': ['울산/앨라배마', '인도/싱가포르', '인도', '인도', '인도'],
        '주요부품': [
            '배터리(192-337), 모터(429-465)',
            '배터리(333-450), ABS 모듈(135-435)',
            '엔진부품(1,420-2,134)',
            '전자제어장치(900-1,000)',
            '차체패널(2,000-2,500)'
        ],
        '월평균생산량': [6500, 7200, 5000, 4800, 7000]
    })
    st.dataframe(current_models, use_container_width=True, hide_index=True)

    st.subheader("⚠️ 생산 위험 모델 알림")
    risk_models = pd.DataFrame({
        '모델명': ['스타리아 LPG', 'Kona EV', 'i10(BA)'],
        '위험등급': ['주의', '중단', '중단'],
        '부족부품': ['LPG 연료계통', '배터리', '엔진 부품'],
        '잔여재고': [45, 0, 12]
    })
    st.dataframe(risk_models.style.applymap(
        lambda x: 'background-color: #ffcccc' if x in ['중단', 0, 12] else '',
        subset=['위험등급', '잔여재고']
    ), use_container_width=True, hide_index=True)

    st.markdown("---")

    st.subheader(" 연도별 생산 추이 분석")
    trend_df = df_inv.groupby(['연도', '공장명'])['재고량'].sum().reset_index()

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.line(trend_df, x='연도', y='재고량', color='공장명', markers=True, title="공장별 생산량 추이")
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.bar(trend_df, x='공장명', y='재고량', color='연도', barmode='group', title="연도별 공장 비교")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader(" 공장별 생산상태 현황")
    plant_status = df_plant.groupby(['공장명', '생산상태']).size().unstack(fill_value=0)
    st.dataframe(plant_status.style.background_gradient(cmap='YlGnBu'), use_container_width=True, hide_index=True)

    with st.expander(" 🗂 원본 데이터 확인"):
        tab1, tab2, tab3 = st.tabs(["차량정보", "재고데이터", "공장데이터"])
        with tab1:
            st.dataframe(df_list, use_container_width=True, hide_index=True)
        with tab2:
            st.dataframe(df_inv, use_container_width=True, hide_index=True)
        with tab3:
            st.dataframe(df_plant, use_container_width=True, hide_index=True)
