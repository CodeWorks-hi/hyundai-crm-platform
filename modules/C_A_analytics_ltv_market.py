# 판매·수출 관리
    # LTV 모델 결과, 시장 트렌드, 예측 분석
        # 시장 트렌드


import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import OneHotEncoder


def preprocess_for_prediction(df):
    # 예측에 필요 없는 정보만 제거
    drop_cols = [
        '연번', '이름', '생년월일', '휴대폰 번호', '이메일', '아이디',
        '가입일', '주소', '고객 평생 가치'  # 예측 대상 포함
    ]
    df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')

    # 결측값 제거 (모델 학습 시에도 적용했다면 동일하게 적용)
    df = df.dropna()

    # 범주형 변수 인코딩
    df = pd.get_dummies(df)

    return df

def ltv_market_ui():

    df = pd.read_csv("data/export_customer_data.csv")

    # 연령대별 평균 LTV 시각화
    fig1 = px.bar(df.groupby("연령대")["고객 평생 가치"].mean().reset_index(),
                  x="연령대", y="고객 평생 가치", title="연령대별 평균 고객 생애 가치")
    st.plotly_chart(fig1, use_container_width=True)

    # 차량 유형별 LTV
    if "최근 구매 제품" in df.columns:
        fig = px.box(df, x="최근 구매 제품", y="고객 평생 가치", title="차량 유형별 고객 가치 분포")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("최근 구매 제품 데이터가 포함되어 있지 않습니다.")

    # 등급별 평균 LTV
    fig3 = px.bar(df.groupby("고객 등급")["고객 평생 가치"].mean().reset_index(),
                  x="고객 등급", y="고객 평생 가치", title="고객 등급별 평균 LTV")
    st.plotly_chart(fig3, use_container_width=True)
