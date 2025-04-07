# 재고 및 공급망 관리
    # 공장/지역별 재고 분포


import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# 차량리스트 데이터 불러오기
car_list_path = "data/hyundae_car_list.csv"
df_list = pd.read_csv(car_list_path)

# 부품 재고 데이터 불러오기
inventory_path = "data/inventory_data.csv"
df_inv = pd.read_csv(inventory_path)

# 누락값 처리
df_inv.fillna(0, inplace=True)

def distribution_ui():
    st.subheader(" 공장별 · 모델별 부품 재고 분포 분석")

    # [1] 공장 좌표 설정
    plant_location = {
        "울산공장": (35.546, 129.317),
        "아산공장": (36.790, 126.977),
        "전주공장": (35.824, 127.148),
        "앨라배마공장": (32.806, -86.791),
        "중국공장": (39.904, 116.407),
        "인도공장": (12.971, 77.594),
        "체코공장": (49.523, 17.642),
        "튀르키예공장": (40.922, 29.330),
        "브라질공장": (-23.682, -46.875),
        "싱가포르공장": (1.352, 103.819),
        "인도네시아공장": (-6.305, 107.097)
    }

    np.random.seed(42) 
    
    # 공장 위치 컬럼 추가
    df_inv["위도"] = df_inv["공장명"].map(lambda x: plant_location.get(x, (0, 0))[0])
    df_inv["경도"] = df_inv["공장명"].map(lambda x: plant_location.get(x, (0, 0))[1])

    # [2] 재고 요약
    summary = df_inv.groupby(
        ["브랜드", "모델명", "모델 구분", "트림명", "차량구분", "연료구분", "공장명", "부품명"]
    )["재고량"].sum().reset_index()
    summary["부족 여부"] = summary["재고량"].apply(lambda x: "이동 필요" if x < 200 else "충분")

    # [3] 공장별 재고량 요약 및 지도 시각화
    plant_inv = df_inv.groupby("공장명")["재고량"].sum().reset_index()
    plant_inv["위도"] = plant_inv["공장명"].map(lambda x: plant_location.get(x, (0, 0))[0])
    plant_inv["경도"] = plant_inv["공장명"].map(lambda x: plant_location.get(x, (0, 0))[1])
    plant_inv["text"] = plant_inv["공장명"] + "<br><b>재고: " + plant_inv["재고량"].astype(int).astype(str) + "</b>"

    with st.expander(" 글로벌 공장 재고 지도 시각화 보기", expanded=True):
        fig = px.scatter_geo(
            plant_inv,
            lat="위도",
            lon="경도",
            size="재고량",
            color="재고량",
            text="text",
            projection="natural earth",
            title="공장별 재고량 시각화"
        )
        fig.update_traces(
            textfont_size=14,
            textposition="top center",
            marker=dict(line=dict(width=1, color='DarkSlateGrey'))
        )
        fig.update_layout(
            geo=dict(
                showland=True,
                landcolor="rgb(240, 240, 240)",
                showcountries=True,
                showcoastlines=True,
                showframe=False
            ),
            height=600,
            margin={"r": 0, "t": 30, "l": 0, "b": 0}
        )
        st.plotly_chart(fig, use_container_width=True)

    # [4] 필터 기능
    with st.expander(" 브랜드 및 모델 필터링", expanded=False):
        brand_list = sorted(df_inv["브랜드"].dropna().unique())
        brand_filter = st.selectbox("브랜드 선택", brand_list)

        model_list = sorted(df_inv[df_inv["브랜드"] == brand_filter]["모델명"].dropna().unique())
        model_filter = st.selectbox("모델명 선택", model_list)

        filtered = summary[
            (summary["브랜드"] == brand_filter) & (summary["모델명"] == model_filter)
        ]
        st.dataframe(filtered, use_container_width=True, hide_index=True)

    # [5] 전체 요약 보기
    with st.expander(" 브랜드/모델/부품별 재고 요약 보기", expanded=True):
        st.dataframe(summary, use_container_width=True, hide_index=True)

    # [6] 🗂 원본 데이터 보기
    with st.expander(" 🗂 원본 데이터 보기", expanded=False):
        st.dataframe(df_list, use_container_width=True, hide_index=True)
