# 탄소 배출량 모니터링
# IGIS 연동 탄소 배출량 모니터링



import pandas as pd
import streamlit as st
import plotly.express as px

@st.cache_data
def load_data():
    return pd.read_csv("data/eco.csv")

def load_restriction_data():
    data = {
        "시도": ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "경기도"],
        "단속대상": ["전국 5등급 차량"] * 6,
        "단속제외대상": [
            "저감장치 부착차량, 긴급자동차, 장애인차량, 국가유공자 등",
            "저감장치 부착차량, 영업용 차량, 기초생활수급자, 차상위 계층",
            "저감장치 부착차량, 영업용 차량, 장애인차량, 소상공인",
            "저감장치 부착차량, 국가유공자 등",
            "저감장치 부착차량, 영업용 차량, 소상공인",
            "저감장치 부착 불가 차량 중 기초생활수급자, 소상공인"
        ],
        "과태료": ["1일 10만원"] * 6
    }
    return pd.DataFrame(data)

def eco_ui():
    st.subheader(" 탄소 배출량 모니터링 (IGIS 연동)")
    st.markdown("차량 수명 주기 내 배출 데이터를 기반으로 친환경 정책 수립에 활용됩니다.")

    df = load_data()

    expected_cols = ["모델명", "차량구분", "차량형태", "연료구분", "엔진형식", "배기량(cc)", "공차중량(kg)", "복합연비(km/L)", "CO₂배출량(g/km)"]
    if not all(col in df.columns for col in expected_cols):
        st.error("❌ 데이터 컬럼명이 예상과 다릅니다.")
        st.write("필요한 컬럼:", expected_cols)
        st.write("현재 컬럼:", list(df.columns))
        return

    df = df.rename(columns={
        "배기량(cc)": "배기량",
        "공차중량(kg)": "공차중량",
        "복합연비(km/L)": "복합연비",
        "CO₂배출량(g/km)": "CO2배출량"
    })

    # 📊 시각화
    top_emitters = df.sort_values(by="CO2배출량", ascending=False).head(10)
    fig1 = px.bar(top_emitters, x="모델명", y="CO2배출량", color="연료구분",
                  title=" CO₂ 배출량 상위 10개 차량 모델")
    st.plotly_chart(fig1, use_container_width=True)

    avg_emissions = df.groupby("연료구분")["CO2배출량"].mean().reset_index()
    fig2 = px.bar(avg_emissions, x="연료구분", y="CO2배출량", title=" 연료 구분별 평균 CO₂ 배출량")
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.box(df, x="차량형태", y="복합연비", color="연료구분", title=" 차량 형태별 복합연비 분포")
    st.plotly_chart(fig3, use_container_width=True)

    # 🧾전체 원본
    with st.expander("📄 전체 원본 데이터 보기"):
        st.dataframe(df, use_container_width=True)

    #  계절관리제 데이터 테이블
    st.markdown("---")
    st.subheader(" 계절관리제 운행제외 대상 정보")
    restriction_df = load_restriction_data()
    st.dataframe(restriction_df, use_container_width=True)

