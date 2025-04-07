import streamlit as st
import pandas as pd
import plotly.express as px

# 데이터 경로 설정
car_list_path = "data/hyundae_car_list.csv"
inventory_path = "data/inventory_data.csv"
customer_path = "data/customer_data.csv"

# 데이터 로드
df_inv = pd.read_csv(inventory_path)
df_list = pd.read_csv(car_list_path)
df_customer = pd.read_csv(customer_path)

def domestic_performance_ui():

    df_customer['통합 연령대'] = df_customer['연령대'].replace(
            {
                '20대 초반': '20대', '20대 중반': '20대', '20대 후반': '20대',
                '30대 초반': '30대', '30대 중반': '30대', '30대 후반': '30대',
                '40대 초반': '40대', '40대 중반': '40대', '40대 후반': '40대',
                '50대 초반': '50대', '50대 중반': '50대', '50대 후반': '50대',
                '60대 초반': '60대 이상', '60대 중반': '60대 이상', 
                '60대 후반': '60대 이상', '70대 초반': '60대 이상'
            }
        )

    col1,col2=st.columns(2)
    # 연도 선택
    with col1:
        years = sorted(df_customer['최근 구매 연도'].unique())
        default_year = 2024
        if default_year in years:
            default_index = years.index(default_year)
        else:
            default_index = len(years) - 1
        year = st.selectbox("연도 선택", years, index=default_index,key='selcet_year')

    # 등급 선택 (전체 옵션 포함)
    with col2:
        # 등급 선택 시 기본 데이터(df_customer)에서 고유 값 가져오기
        grade_options = sorted(df_customer['고객 그룹'].unique().tolist())
        selected_grade = st.selectbox("등급 선택", options=['전체'] + grade_options, index=0, key="grade_selectbox")

    # 데이터 필터링
    df_filtered = df_customer[df_customer['최근 구매 연도'] == year]  # 연도로 필터링
    if selected_grade != '전체':
        df_filtered = df_filtered[df_filtered['고객 그룹'] == selected_grade]  # 등급으로 추가 필터링


    # 주요 지표 계산
    total_customers = df_filtered['아이디'].nunique()  # 고유 고객 수 계산
    avg_age = round(df_filtered['현재 나이'].mean(), 2) if not df_filtered.empty else "-"  # 평균 나이 계산
    total_sales = len(df_filtered)  # 총 판매량 계산

    # 전년대비 판매 증가율 계산
    if year - 1 in years:
        last_year_sales = len(df_customer[df_customer['최근 구매 연도'] == year - 1])  # 전년도 판매량 계산
        if last_year_sales > 0:
            YoY_growth = round(((total_sales - last_year_sales) / last_year_sales) * 100, 2)
        else:
            YoY_growth = 0  # 전년도 판매량이 0일 경우 증가율을 0으로 설정
    else:
        YoY_growth = "-"  # 전년도 데이터가 없을 경우

    # 주요 지표 표시 (카드 스타일)
    st.markdown("### 주요 지표")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 고객 수", f"{total_customers} 명")
    col2.metric("평균 연령", f"{avg_age:.1f} 세" if isinstance(avg_age, (int, float)) else f"{avg_age} 세")
    col3.metric("전년대비 판매 증가율", f"{YoY_growth:.2f}%" if isinstance(YoY_growth, (int, float)) else f"{YoY_growth}")
    col4.metric("총 판매량", f"{total_sales} 대")


    # 분포 시각화 (깔끔한 레이아웃)
    st.markdown("---")


    # 고객 그룹 분포 계산
    grade_counts = df_filtered['고객 그룹'].value_counts()

    # 하단 시각화 영역
    col1, col2 = st.columns(2)

    

    with col1:
        # 차량 모델 구매 비율 계산
        model_counts = df_filtered['최근 구매 제품'].value_counts()

        if model_counts.empty:
            st.write("필터링된 데이터가 없습니다.")
        else:
            # Plotly 원형 차트 시각화 (차량 모델 구매 비율)
            fig = px.pie(
                names=model_counts.index,
                values=model_counts.values,
                title="차량 분포",
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            # 숫자 표시 제거
            fig.update_traces(textinfo='none')
            
            # 그래프 출력
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        # 월별 판매량 계산
        if '최근 구매 날짜' in df_filtered.columns:
            df_filtered['구매 월'] = pd.to_datetime(df_filtered['최근 구매 날짜']).dt.month  # 월 추출
            monthly_sales = df_filtered['구매 월'].value_counts().sort_index()  # 월별 판매량 집계

            if monthly_sales.empty:
                st.write("필터링된 데이터가 없습니다.")
            else:
                # Plotly 막대 차트 시각화 (월별 판매량)
                fig = px.line(
                    x=monthly_sales.index,
                    y=monthly_sales.values,
                    labels={'x': "월", 'y': "판매량"},
                    title="월별 판매량",
                    markers=True # 각 데이터 포인트에 값 추가
                )
               
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("날짜 데이터가 없습니다.")

    col1,col2=st.columns(2)
    with col1:
        with st.expander("가장 많이 판매된 차종 (TOP 3)", expanded=False):
            # 차량 모델 구매 비율 데이터를 내림차순으로 정렬하고 상위 3개만 추출
            sorted_model_counts = model_counts.sort_values(ascending=False).head(3)
            st.dataframe(sorted_model_counts)

    with col2:
        with st.expander("가장 많이 팔린 월 (TOP 3)", expanded=False):
            # 월별 판매량 데이터를 내림차순으로 정렬하고 상위 3개만 추출
            sorted_monthly_sales = monthly_sales.sort_values(ascending=False).head(3)
            st.dataframe(sorted_monthly_sales)
            