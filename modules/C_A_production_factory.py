import streamlit as st
import pandas as pd
import plotly.express as px



# 데이터 로드 함수
@st.cache_data
def load_data():
    df_inv = pd.read_csv("data/inventory_data.csv")
    df_list = pd.read_csv("data/hyundae_car_list.csv")
    
    # 데이터 정제
    df_inv['트림명'] = df_inv['트림명'].str.strip()
    df_list['트림명'] = df_list['트림명'].str.strip()
    return df_inv, df_list

# 생산 분석 리포트 생성 함수
def create_production_report(df_inv):
    with st.spinner("생산 분석 데이터 처리 중..."):
        # 생산 가능 수량 계산
        prod_capacity = df_inv.groupby(['공장명', '모델명', '트림명'])['재고량'].min()
        total_prod = prod_capacity.groupby('공장명').sum().reset_index(name='생산가능수량')
        
        # 재고 분석
        inventory_analysis = df_inv.groupby('공장명').agg(
            총재고량=('재고량', 'sum'),
            평균재고=('재고량', 'mean'),
            고유부품수=('부품명', 'nunique')
        ).reset_index()
        
        # 리포트 생성 및 타입 변환
        report = pd.merge(total_prod, inventory_analysis, on='공장명')
        report['생산효율'] = (report['생산가능수량'] / report['총재고량'] * 100)\
                             .round(2)\
                             .astype('float64')
        
        report = report.astype({
            '생산가능수량': 'int32',
            '총재고량': 'int32',
            '고유부품수': 'int32'
        })
        
        return report


# 부품 트리맵 생성 함수
def create_parts_treemap(df_inv):
    part_inventory = df_inv.groupby(['공장명', '부품명'])['재고량'].sum().reset_index()
    return px.treemap(
        part_inventory, 
        path=['공장명', '부품명'], 
        values='재고량',
        color='재고량', 
        color_continuous_scale='Blues',
        height=800
    )

def factory_ui():
    df_inv, df_list = load_data()
    factory_report = create_production_report(df_inv)
    
    # 대시보드 헤더
    st.title(" 현대자동차 생산 현황 실시간 모니터링 시스템")
    
    # 핵심 지표
    cols = st.columns(4)
    metrics_style = "<style>.stMetric {padding: 20px; background-color: #f8f9fa; border-radius: 10px;}</style>"
    st.markdown(metrics_style, unsafe_allow_html=True)
    
    cols[0].metric("총 부품 재고", f"{factory_report['총재고량'].sum():,}개", help="전체 공장의 부품 재고 총합")
    cols[1].metric("최대 생산 가능", 
                f"{factory_report['생산가능수량'].max():,}대", 
                factory_report.loc[factory_report['생산가능수량'].idxmax(), '공장명'])
    cols[2].metric("최고 생산 효율", 
                f"{factory_report['생산효율'].max()}%", 
                factory_report.loc[factory_report['생산효율'].idxmax(), '공장명'])
    cols[3].metric("평균 회전율", 
                f"{factory_report['생산효율'].mean():.1f}%", 
                help="전체 공장의 평균 재고 회전율")

    # 메인 탭 구성
    tab1, tab2, tab3 = st.tabs([" 생산 능력 분석", "부품 재고 현황", " 공장별 상세 리포트"])
    
    with tab1:
        col1, col2 = st.columns([3, 2])
        with col1:
            fig = px.bar(
                factory_report.sort_values('생산가능수량', ascending=False),
                x='공장명', 
                y=['생산가능수량', '총재고량'],
                title="<b>공장별 생산 능력 vs 재고량 비교</b>",
                labels={'value': '수량', 'variable': '구분'},
                barmode='group',
                height=600
            )
            fig.update_layout(font=dict(size=14))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig2 = px.scatter(
                factory_report, 
                x='총재고량', 
                y='생산효율',
                size='고유부품수', 
                color='공장명',
                title="<b>재고량 대비 생산효율 분포</b>",
                hover_data=['평균재고'],
                height=600
            )
            fig2.update_traces(marker=dict(size=14))
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("공장-부품 계층적 재고 분포", divider='blue')
            fig3 = create_parts_treemap(df_inv)
            st.plotly_chart(fig3, use_container_width=True)
            
        with col2:
            with st.expander(" 부품별 상세 데이터", expanded=True):
                st.dataframe(
                    df_inv[['부품명', '공장명', '재고량']]
                    .groupby(['부품명', '공장명'])
                    .sum()
                    .reset_index()
                    .sort_values('재고량', ascending=False),
                    column_config={
                        "부품명": "부품종류",
                        "공장명": "생산공장",
                        "재고량": st.column_config.ProgressColumn(
                            "현재고",
                            format="%d개",
                            min_value=0,
                            max_value=df_inv['재고량'].max()
                        )
                    },
                    height=600,
                    use_container_width=True,
                    hide_index=True
                )

        critical_parts = df_inv[df_inv['부품명'].isin(['배터리', '모터', 'ABS 모듈'])]
        pivot_table = critical_parts.pivot_table(
            index='부품명', 
            columns='공장명', 
            values='재고량', 
            aggfunc='sum'
        ).fillna(0).astype(int)
        
        st.subheader(" 핵심 부품 현황", divider='orange')
        st.dataframe(
            pivot_table.style.format("{:,}")
              .background_gradient(cmap='YlGnBu', axis=1),
            height=200,
            use_container_width=True
        )
        
        # 재고 경고 시스템
        min_stocks = critical_parts.groupby('부품명')['재고량'].min()
        for part, qty in min_stocks.items():
            if qty < 100:
                st.error(f"⚠️ {part} 최소재고 위험: {qty:,}개 (권장 ≥100)", icon="🚨")

    with tab3:
        selected_factory = st.selectbox(
            '공장 선택', 
            df_inv['공장명'].unique(),
            key='factory_select'
        )
        
        factory_data = df_inv[df_inv['공장명'] == selected_factory]
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
            st.subheader(f" {selected_factory} 부품 현황", divider='green')
            st.dataframe(
                parts_summary.style.format("{:,}")
                  .background_gradient(subset=['총재고'], cmap='Blues'),
                height=600,
                use_container_width=True
            )
        
        with col2:
            st.subheader(f" {selected_factory} 재고 분포", divider='green')
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

        with st.expander(" 원본 데이터 확인", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("차량 마스터 데이터", divider='gray')
                st.dataframe(
                    df_list,
                    column_config={"img_url": st.column_config.ImageColumn()},
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


