# 판매·수출 관리
    # 판매·수출 관리 
        # 국내 판매 (차종/지역별 등)
            # 지역별 시장 비교



import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def domestic_region_ui():
    st.subheader("판매·수출 관리")
    st.write("국내 판매 실적을 분석하는 페이지입니다.")
    st.write("차종/지역별 시장 비교")

    st.header('지역별 비교')

    df=pd.read_csv('./data/customer_data.csv')

    # 지역으로 그룹화해서 갯수 세기
    region=df.groupby('거주 지역')[['최근 구매 제품']].count().reset_index()
    
    # 지역별 최근 구매 제품 분포 보기
    region_car=df.groupby(['거주 지역','최근 구매 제품'])[['최근 거래 금액']].count().reset_index()
    region_car=region_car.pivot_table(index='거주 지역',columns='최근 구매 제품',values='최근 거래 금액',fill_value=0).reset_index()
    region_car.columns.name=None

    

    col1, col2=st.columns(2)
    with col1:
        # 시각화 
        fig1, ax = plt.subplots(figsize=(9, 6))
        ax.bar(region['거주 지역'], region['최근 구매 제품'], color='pink')
        ax.set_title('거주 지역별 판매량')
        ax.set_xlabel('거주 지역')
        ax.set_ylabel('판매량')
        ax.tick_params(axis='x', rotation=45)

        st.pyplot(fig1)

    with col2:
        # 히트맵으로 시각화
        fig2, ax = plt.subplots(figsize=(10, 7))
        sb.heatmap(
            region_car.set_index("거주 지역"),
            annot=True,
            cmap="YlGnBu",
            cbar=True,
            ax=ax
        )
        ax.set_title("지역별 차량 구매 데이터 히트맵")
        ax.set_xlabel("차량 모델")
        ax.set_ylabel("거주 지역")
        plt.xticks(rotation=45)
        plt.tight_layout()

        st.pyplot(fig2)
