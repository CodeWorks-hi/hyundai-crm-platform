# 판매·수출 관리
    # 판매·수출 관리 
        # 국내 판매 (차종/지역별 등)
            # 지역별 시장 비교



import streamlit as st
import pandas as pd
import plotly.express as px





customer_path = "data/customer_data.csv"
df_customer = pd.read_csv(customer_path)

def domestic_region_ui():

    col1, col2=st.columns(2)
    # 연도 선택
    with col1:
        years = sorted(df_customer['최근 구매 연도'].unique())
        default_year = 2024
        default_index = years.index(default_year) if default_year in years else 0
        year = st.selectbox("연도 선택", years, index=default_index)

    # 지역 선택
    with col2:
        regions = sorted(df_customer['거주 지역'].unique())
        default_region = '서울특별시'
        default_region_index = regions.index(default_region) if default_region in regions else 0
        region = st.selectbox("지역 선택", regions, index=default_region_index)

    # 데이터 필터링 (연도 및 지역 기준)
    df_filtered = df_customer[
        (df_customer['최근 구매 연도'] == year) &
        (df_customer['거주 지역'] == region)
    ]

    # 주요 지표 계산
    if not df_filtered.empty:
        total_sales = df_filtered['최근 구매 제품'].count()  # 총 판매량
        total_money = df_filtered['최근 거래 금액'].sum()  # 총 판매 금액

        # 선택한 연도와 지역에 대한 전년 대비 판매 증가율 계산
        YoY_growth = "-"

        if year - 1 in years:
            # 현재 연도와 전년도 데이터 필터링
            current_year_sales = df_customer[
                (df_customer['최근 구매 연도'] == year) & (df_customer['거주 지역'] == region)
            ]
            last_year_sales = df_customer[
                (df_customer['최근 구매 연도'] == year - 1) & (df_customer['거주 지역'] == region)
            ]

            # 현재 연도와 전년도 판매량 계산
            current_sales = len(current_year_sales)
            previous_sales = len(last_year_sales)

            # 증가율 계산
            if previous_sales > 0:
                YoY_growth = round(((current_sales - previous_sales) / previous_sales) * 100, 2)
                YoY_growth = f"{YoY_growth} %"
            else:
                YoY_growth = "- %"


        # 주요 지표 표시
        st.markdown("### 주요 지표")
        col1, col2, col3 = st.columns(3)
        col1.metric(label="총 판매량", value=f"{total_sales} 대")
        col2.metric(label="총 판매 금액", value=f"{total_money:,} 원")
        col3.metric(label=f"{region} - 작년 대비 판매 증가율", value=f"{YoY_growth}")

    else:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")

    # 원본 데이터 보기 (확장 가능)
    with st.expander("원본 데이터 보기", expanded=False):
        if df_filtered.empty:
            st.write(f"{year}년, {region}에 해당하는 데이터가 없습니다.")
        else:
            st.write(f"{year}년, {region}에 대한 데이터를 분석합니다.")
            st.write(df_filtered)
    

    st.markdown("---")

    # 아래부터 위에 선택에 영향 없음
    
    col1,col2=st.columns(2)
    with col1:
        # 지역별 총 판매량 비교 (막대)
        # 지역별 총 판매량 계산
        region_sale = df_customer.groupby('거주 지역')['최근 구매 제품'].count().reset_index()
        region_sale.columns = ['거주 지역', '판매량']

        # Streamlit에서 출력
        st.markdown("### 지역별 총 판매량 비교")

        # Plotly로 막대 그래프 생성
        fig = px.bar(
            region_sale,
            x='거주 지역',
            y='판매량',
            labels={'판매량': '판매량', '거주 지역': '지역'},
            color='거주 지역',
            text_auto=False,
            color_discrete_sequence=px.colors.sequential.RdBu
        )

        # Streamlit에서 그래프 표시
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # 지역별 점유율 계산
        region_sale = df_customer.groupby('거주 지역')['최근 구매 제품'].count()
        region_sale_percentage = (region_sale / region_sale.sum() * 100).round(2).reset_index()
        region_sale_percentage.columns = ['거주 지역', '점유율 (%)']

        # Streamlit에서 출력
        st.markdown("### 지역별 점유율 비교")

        # Plotly로 원형 그래프 생성
        fig = px.pie(
            region_sale_percentage,
            names='거주 지역',
            values='점유율 (%)',
            color_discrete_sequence=px.colors.sequential.RdBu
        )

        # 숫자 표시 제거
        fig.update_traces(textinfo='none')

        # Streamlit에서 그래프 표시
        st.plotly_chart(fig)

    col1, col2=st.columns(2)
    with col1:
        # 지역별 총 판매량 계산
        region_sales = df_customer.groupby('거주 지역')['최근 구매 제품'].count().reset_index()
        region_sales.columns = ['거주 지역', '판매량']

        # 전체 판매량 대비 점유율 계산
        region_sales['점유율 (%)'] = (region_sales['판매량'] / region_sales['판매량'].sum() * 100).round(2)

        # 판매량 기준 상위 3개 지역 추출
        top3_regions = region_sales.sort_values(by='판매량', ascending=False).head(3)

        # Streamlit에서 출력
        with st.expander("판매 상위 지역 TOP3", expanded=False):
            st.write(top3_regions)
            
    with col2:
        # 지역별 총 판매량 계산
        region_sales = df_customer.groupby('거주 지역')['최근 구매 제품'].count().reset_index()
        region_sales.columns = ['거주 지역', '판매량']

        # 전체 판매량 대비 점유율 계산
        region_sales['점유율 (%)'] = (region_sales['판매량'] / region_sales['판매량'].sum() * 100).round(2)

        # 판매량 기준 하위 3개 지역 추출
        bottom3_regions = region_sales.sort_values(by='판매량', ascending=True).head(3)

        # Streamlit에서 출력
        with st.expander("판매 하위 지역 TOP3", expanded=False):
            st.write(bottom3_regions)

    # 지역에 따른 차종 히트맵
    col1,col2=st.columns(2)
    with col1:
        # 지역별 차종 빈도 계산
        heatmap_data = df_customer.groupby(['거주 지역', '최근 구매 제품'])['아이디'].count().unstack().fillna(0)

        # Plotly로 히트맵 생성
        fig = px.imshow(
            heatmap_data,
            labels=dict(x="차종", y="거주 지역", color="빈도"),
            x=heatmap_data.columns,
            y=heatmap_data.index,
            text_auto=False,
            color_continuous_scale="Blues"
        )

        # 히트맵 크기 조정 (더 크게 설정)
        fig.update_layout(
            width=800,  # 가로 크기 설정
            height=600  # 세로 크기 설정
        )

        # Streamlit에서 히트맵 출력
        st.markdown("### 지역별 차종 히트맵")
        st.plotly_chart(fig, use_container_width=True)

    
    with col2:
        st.markdown("### 지역별 차종 비율")

        selected_region = st.selectbox("지역을 선택하세요", df_customer['거주 지역'].unique())

        # 선택한 지역의 데이터 필터링
        filtered_data = df_customer[df_customer['거주 지역'] == selected_region]

        # 차종 비율 계산
        car_type_ratio = filtered_data.groupby('최근 구매 제품')['아이디'].count().reset_index()
        car_type_ratio.columns = ['차종', '비율 (%)']
        car_type_ratio['비율 (%)'] = (car_type_ratio['비율 (%)'] / car_type_ratio['비율 (%)'].sum() * 100).round(2)

        # 원형 그래프 시각화
        
        fig = px.pie(
            car_type_ratio,
            names='차종',
            values='비율 (%)',
            color_discrete_sequence=px.colors.sequential.RdBu
        )

        # 숫자 표시 제거
        fig.update_traces(textinfo='none')

        st.plotly_chart(fig)


    col1,col2=st.columns(2)
    with col1:
        # 지역별 차종 빈도 계산
        region_top_car = (
            df_customer.groupby(['거주 지역', '최근 구매 제품'])['아이디'].count()
            .reset_index()
            .rename(columns={'아이디': '판매량'})
        )

        # 각 지역에서 가장 많이 판매된 차종 추출
        top_car_per_region = region_top_car.loc[
            region_top_car.groupby('거주 지역')['판매량'].idxmax()
        ].reset_index(drop=True)

        # Streamlit에서 출력
        with st.expander("각 지역에서 가장 많이 판매된 차종", expanded=False):
            st.dataframe(top_car_per_region)

    with col2:  
        # Streamlit에서 출력
        with st.expander(f"{selected_region} 지역의 차종 비율 데이터", expanded=False):
            st.write(car_type_ratio)
