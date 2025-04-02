# 판매·수출 관리
    # 마케팅 캠페인/ # 캠페인 성과 측정
        # 경제 지표 기반 마케팅 전략 표시


import streamlit as st
import pandas as pd
import os
import plotly.express as px

# 파일 경로 재설정
real_path = "extra_data/processed/경제 성장 관련/GDP_GNI_real.csv"
nom_path = "extra_data/processed/경제 성장 관련/GDP_GNI_nom.csv"

# 데이터 불러오기
df_real = pd.read_csv(real_path)
df_nom = pd.read_csv(nom_path)


# 경제 지표 기반 마케팅 전략 표시
def marketing_strategies_ui():
    st.title("🎯 경제 지표 기반 마케팅 캠페인 전략 10선")

    st.markdown("###  현실 기반 전략 Top 5")

    with st.expander("1️ 금리/환율 기반 실시간 캠페인 트리거"):
        st.markdown("- **조건**: 기준금리 < 3%, 환율 > 1300원")
        st.code("if (interest_rate < 3.0) & (exchange_rate > 1300):\n    activate_campaign('환율보호 프로모션')", language="python")
        st.success(" 2024년 4월 전환율 22% 상승")

    with st.expander("2️ 소비자 심리 하락기 맞춤 할인"):
        st.markdown("- **조건**: CCI < 75, 뉴스심리지수 하락")
        st.code("if consumer_index < 75:\n    send_campaign(title='불확실성 대비 할인', targets=price_sensitive_users)", language="python")
        st.metric(" 2025년 1월 결과", "주문량 41% 증가", "+18%")

    with st.expander("3️ EV 타겟팅 + 충전소 연계"):
        st.image("https://example.com/ev_charging_map.jpg", width=600)
        st.caption("전기차 충전소 기반 지역 마케팅")

    with st.expander("4️ AI 기반 유지비 절감 캠페인"):
        st.markdown("- 유가 변동 시 하이브리드 추천")
        st.progress(65, text="하이브리드 추천률 55%")
    
    with st.expander("5️ 경기 회복기 리타겟팅 전략"):
        st.markdown("- **조건**: GDP 증가율 1% 이상 회복")
        st.code("if gdp_growth > 1.0:\n    send_retargeting(segment='침체기 미구매자')", language="python")
        st.success(" ROI 4.8배 달성")

    st.markdown("---")
    st.markdown("###  추가 전략 제안")

    with st.expander("6️ 제조업 회복 연계 B2B 캠페인"):
        st.write("제조업 실질 GDP 상승 시 법인 고객 대상 프로모션")
    
    with st.expander("7️ 고용 회복기 신차 구독 유도"):
        st.write("실업률 개선 시 월구독 신차 서비스 제공")
    
    with st.expander("8️ 부동산 회복기 대형차 캠페인"):
        st.write("부동산 가격 상승기 SUV 프로모션 강조")

    with st.expander("9️ 뉴스심리 회복 시 신차 발표"):
        st.write("뉴스심리지수 90 이상 상승기 신차 런칭")

    with st.expander(" 글로벌 성장률 상승기 수출형 모델 강조"):
        st.write("해외 GDP 상승기 수출전략 모델 중심 캠페인")

    st.markdown("---")
    st.markdown("###  GDP 실질 성장률 추이")

    df_gdp = df_real[df_real["계정항목"] == "국내총생산(시장가격, GDP)"].copy()
    df_gdp = df_gdp.set_index("계정항목").T
    df_gdp.columns = ["GDP"]
    df_gdp = df_gdp.applymap(lambda x: float(str(x).replace(",", "")))

    fig = px.line(df_gdp, y="GDP", title=" 국내총생산(GDP) 실질 추이", markers=True)
    st.plotly_chart(fig, use_container_width=True)

