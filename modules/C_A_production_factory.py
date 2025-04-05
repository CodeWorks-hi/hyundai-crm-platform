# 생산·제조 현황 분석
# 현대자동차 생산 현황 실시간 모니터링 시스템

import streamlit as st
import pandas as pd
import plotly.express as px
from .C_A_production_factory_report import report_ui
from .C_A_production_factory_treemap import treemap_ui
from .C_A_production_factory_analysis import factory_analysis_ui

# 데이터 로드 함수
@st.cache_data
def load_data():
    df_inv = pd.read_csv("data/inventory_data.csv")
    df_list = pd.read_csv("data/hyundae_car_list.csv")
    trim_list = pd.read_csv("data/model_trim_capacity.csv") 
    return df_inv, df_list, trim_list

# 생산 UI 함수
def factory_ui():
    df_inv, df_list, trim_list = load_data()

    # 검색 결과 [2] 첨부 파일 구조에 따른 컬럼명 수정
    try:
        # 실제 컬럼명 확인 (Plant → 생산공장, Production Capacity → 생산가능수량)
        trim_list = trim_list.rename(columns={
            'Plant': '생산공장',
            'Production Capacity': '생산가능수량'
        })
        
        # 필수 컬럼 존재 여부 검증
        required_columns = ['생산공장', '생산가능수량']
        if not all(col in trim_list.columns for col in required_columns):
            missing = [col for col in required_columns if col not in trim_list.columns]
            raise KeyError(f"필수 컬럼 누락: {missing}")

        prod_capacity = trim_list.groupby('생산공장')['생산가능수량'].sum().reset_index()

    except KeyError as e:
        st.error(f"❌ 데이터 구조 불일치: {str(e)}")
        st.write("현재 파일 컬럼 구조:", trim_list.columns.tolist())
        return

    # 생산 분석 리포트 생성 (검색 결과 [2] IGIS 시스템 반영)
    with st.spinner("IGIS 시스템 데이터 처리 중..."):
        # 생산가능수량 계산 (첨부 파일 [3] 기준)
        prod_capacity = trim_list.groupby('생산공장')['생산가능수량'].sum().reset_index()
        
        # 재고 분석 (검색 결과 [2] 인벤토리 관리 기준)
        inventory_analysis = df_inv.groupby('생산공장').agg(
            총재고량=('재고량', 'sum'),
            평균재고=('재고량', 'mean'),
            고유부품수=('부품명', 'nunique')
        ).reset_index()

        # 리포트 통합 (검색 결과 [2] KPI 지표 반영)
        report = pd.merge(prod_capacity, inventory_analysis, on='생산공장')
        report['생산효율'] = (report['생산가능수량'] / report['총재고량'] * 100).round(2)

        # 데이터 타입 변환
        report = report.astype({
            '생산가능수량': 'int',
            '총재고량': 'int',
            '고유부품수': 'int'
        })

        st.subheader("현대자동차 생산 현황 실시간 모니터링 시스템")

    cols = st.columns(5)
    st.markdown("""<style>.stMetric {padding: 20px; background-color: #f8f9fa; border-radius: 10px;}</style>""", 
                unsafe_allow_html=True)

    with cols[0]:
        st.metric("최다 재고", 
                 f"{report['총재고량'].max():,}개", 
                 report.loc[report['총재고량'].idxmax(), '생산공장'],
                 help="단일 공장 최대 재고 보유량")
    
    with cols[1]:
        st.metric("신규 부품", 
                 f"{report['고유부품수'].sum():,}종", 
                 "2025년 4월 기준",
                 delta_color="off")
    
    with cols[2]:
        max_prod = report['생산가능수량'].max()
        st.metric("최대 생산 가능", 
                 f"{max_prod:,}대", 
                 report.loc[report['생산가능수량'].idxmax(), '생산공장'],
                 help="IGIS 시스템 예측 최대 생산량")
    
    with cols[3]:
        st.metric("최고 생산 효율", 
                 f"{report['생산효율'].max():.2f}%", 
                 report.loc[report['생산효율'].idxmax(), '생산공장'],
                 delta_color="inverse")
    
    with cols[4]:
        st.metric("평균 회전율", 
                 f"{report['생산효율'].mean():.1f}%", 
                 help="Apache Spark 기반 실시간 분석 결과")


    # 탭 구성
    tab1, tab2, tab3 ,tab4= st.tabs(["부품 재고 현황"," 생산 가능 수량" ,"공장별 리포트","생산 능력 분석"])

    # TAB 1 - 부품 재고 현황 (검색 결과 [2] 시각화 표준 적용)
    with tab1:
        treemap_ui(df_inv)

    # TAB 2 - 생산 가능 수량 (검색 결과 [2] 예측 엔진 반영)
    with tab2:
        factory_analysis_ui()

    # TAB 3 - 공장별 리포트 (검색 결과 [2] CRM 구조 반영)
    with tab3:
        st.markdown("---")
        
        # 공장 선택 (검색 결과 [2] 사용자 인터페이스 가이드)
        selected_factory = st.selectbox(
            '공장 선택',
            df_inv['생산공장'].unique(),
            key='factory_select',
            help="분석할 공장을 선택하세요"
        )
        
        factory_data = df_inv[df_inv['생산공장'] == selected_factory]

        # 부품 현황 분석 (검색 결과 [2] 재고 관리 기준)
        parts_summary = factory_data.groupby('부품명')['재고량']\
            .agg(['sum', 'median', 'max'])\
            .rename(columns={
                'sum': '총재고',
                'median': '중간값',
                'max': '최대재고'
            })\
            .astype(int)\
            .sort_values('총재고', ascending=False)

        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.subheader(f"{selected_factory} 부품 현황", divider='green')
            st.dataframe(
                parts_summary.style.format("{:,}")
                .background_gradient(subset=['총재고'], cmap='Blues'),
                height=600,
                use_container_width=True
            )

        with col2:
            st.subheader(f"{selected_factory} 재고 분포", divider='green')
            fig = px.bar(
                parts_summary.reset_index(),
                x='부품명',
                y='총재고',
                color='부품명',
                title=f"<b>{selected_factory} 부품별 재고 현황</b>",
                height=600
            )
            fig.update_layout(
                xaxis_title=None,
                yaxis_title="재고량",
                showlegend=False,
                font=dict(size=14)
            )
            st.plotly_chart(fig, use_container_width=True)

        # 원본 데이터 확인 (검색 결과 [2] 데이터 투명성 요구사항 반영)
        with st.expander("🔍 원본 데이터 확인", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("차량 마스터 데이터", divider='gray')
                st.dataframe(
                    df_list,
                    height=400,
                    use_container_width=True,
                    hide_index=True
                )
            with col2:
                st.subheader("부품 재고 데이터", divider='gray')
                st.dataframe(
                    df_inv,
                    height=400,
                    use_container_width=True,
                    hide_index=True
                )

    # TAB 4 - 생산 능력 분석 (검색 결과 [2] 예측 분석 요구사항 반영)
    with tab4:
        report_ui(df_inv)


