import streamlit as st
import pandas as pd
import plotly.express as px

customer_path = "data/domestic_customer_data.csv"
df_customer = pd.read_csv(customer_path)


def domestic_growth_ui():
    col1,col2,col3=st.columns(3)
    with col1:
        years = sorted(df_customer['구매연도'].unique())
        selected_year = st.selectbox("연도 선택", years)

    with col2:
        regions = ['전체'] + sorted(df_customer['거주 지역'].unique())  # '전체' 옵션 추가
        selected_region = st.selectbox("지역 선택", regions)

    with col3:
        categorys = ['전체'] + sorted(df_customer['모델명'].unique())  # '전체' 옵션 추가
        selected_category = st.selectbox("차종 선택", categorys)


    # 필터링 로직
    filtered_data = df_customer[df_customer['구매연도'] == selected_year]  # 선택한 연도로 필터링

    if selected_region != '전체':
        filtered_data = filtered_data[filtered_data['거주 지역'] == selected_region]

    if selected_category != '전체':
        filtered_data = filtered_data[filtered_data['모델명'] == selected_category]

    # 월별 구매량 계산
    monthly_trend_data = filtered_data.groupby('구매월')['연락처'].count()

    # 성장률 계산
    monthly_growth_rate = monthly_trend_data.pct_change().fillna(0) * 100

    # 시각화 데이터 준비
    if monthly_growth_rate.empty:
        st.write("필터링된 데이터가 없습니다.")
    else:
        
        # Plotly 라인 차트 시각화
        fig = px.line(
            x=monthly_growth_rate.index,
            y=monthly_growth_rate.values,
            labels={'x': "월", 'y': "성장률 (%)"},
            title=f"{selected_year}년 {selected_region} 지역 {selected_category} 월별 성장률",
            markers=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
        ---
        ##### 📊 분석 개요
        선택한 조건(연도, 지역, 차종)에 따른 **국내 판매 월별 성장률**을 시각적으로 분석합니다.

        ##### 🔍 분석 세부 결과
        - 월별 판매 실적 데이터를 기반으로 **성장률(%)**을 산출하였습니다.
        - **연속적인 월별 비교**를 통해 특정 시기나 이벤트에 따른 성과 변동을 파악할 수 있습니다.
        - 지역 및 차종 선택 시 해당 조건에 맞는 세부 분석 결과가 반영됩니다.

        ##### 📈 성장률 해석 기준
        | 성장률 (%) | 의미             | 예시 해석                       |
        |------------|------------------|----------------------------------|
        | > 0        | 판매 증가 📈     | 전월 대비 실적 향상              |
        | = 0        | 변화 없음 ➖     | 전월과 동일한 수준               |
        | < 0        | 판매 감소 📉     | 전월 대비 실적 감소              |

        ##### 🧭 활용 방안
        1. **감소 구간**에 대해 원인을 분석하고 개선 전략을 수립할 수 있습니다.
        2. **급격한 증가 구간**은 성공 요인을 도출해 마케팅/판매 전략에 반영 가능합니다.
        3. 특정 지역·차종의 성과를 비교하여 **지역 맞춤 전략** 수립에 활용할 수 있습니다.
    """)

    st.markdown("###### ")

    # 원본 데이터 보기
    with st.expander("🗂 원본 데이터 보기"):
        st.dataframe(df_customer, use_container_width=True, hide_index=True)