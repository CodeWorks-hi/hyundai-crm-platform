# 고객 메인 대시보드   
    # 이벤트 및 공지사항



import streamlit as st
import pandas as pd
import plotly.express as px

def event_ui():
    if st.button("← 유저 메인으로 돌아가기", key="back_to_user_main"):
        st.session_state.current_page = "user_main"
        st.rerun()
    st.subheader("📣 이벤트 및 공지사항")

    st.markdown("#### 📌 최근 공지사항")
    st.info("🚗 [공지] 6월부터 캐스퍼 일렉트릭 예약 판매 시작합니다.")
    st.warning("🛠️ [점검안내] 5월 10일 02:00~05:00 시스템 점검 예정입니다.")

    st.markdown("---")

    st.markdown("#### 🎁 현재 진행 중인 이벤트")
    st.success("신규 방문고객 대상 시승 이벤트 - 5월 1일부터 5월 31일까지!")


    # 카드사 혜택 데이터
    benefit_data = {
        "카드사": ["현대카드", "롯데카드", "우리카드", "하나카드"],
        "할부 혜택 (최대 개월 수)": [60, 36, 48, 60],
        "포인트 적립 (%)": [5, 3, 4, 2],
        "주유비 할인 (%)": [7, 5, 6, 5],
        "전기차 충전 혜택 (%)": [10, 4, 8, 6]
    }
    benefit_df = pd.DataFrame(benefit_data)

    # Melt 변환
    benefit_melted = benefit_df.melt(id_vars=["카드사"], var_name="혜택 유형", value_name="비율")

    # Plotly 바 차트
    fig = px.bar(
        benefit_melted, x="카드사", y="비율", color="혜택 유형",
        barmode="group", title="카드사별 주요 혜택 비교",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', font=dict(size=14),
        xaxis_title="카드사", yaxis_title="혜택 비율 / 개월 수",
        yaxis=dict(range=[0, 65]), legend_title="혜택 유형"
    )
    fig.update_traces(textposition='outside', texttemplate='%{value}')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 카드사 제휴 장점
    col1, col2 = st.columns(2)
    with col1:
        st.header("카드사 제휴 확대 이점")
        st.markdown("""
        **1. 고객 구매력 강화**  
        - 전략적 제휴 통한 판매 촉진  
        - 장기 무이자 할부로 구매 장벽 해소  
        - 포인트 적립 프로그램 운영  

        **2. 유지비 절감**  
        - 보험/정비/주유 할인 혜택  
        - 전기차 충전 할인
        """)

    with col2:
        st.header("카드사 제휴 확대 예시")
        st.markdown("""
        - **현대/롯데/우리/하나카드 제휴**  
        - 맞춤형 할부 & 포인트 혜택 제공  
        - 할인 혜택 + 프로모션 연계  
        - 전용 카드 혜택으로 브랜드 충성도 상승
        """)

    st.markdown("---")

    # 카드사별 상세 혜택 테이블
    data = {
        "카드사": ["현대카드", "롯데카드", "우리카드", "하나카드"],
        "주요혜택": [
            "VIP 정비 쿠폰 제공",
            "렌터카 할인 + 5% 캐시백",
            "전용 카드 + 추가 할인(3~5%)",
            "60개월 할부 + 프리미엄 혜택"
        ],
        "공통혜택": [
            "무이자 할부, 포인트 적립, EV 충전소 할인",
            "최대 36개월 할부 + 유지비 절감",
            "EV 혜택, 주유비 할인",
            "보험/정비/주유비 절감 혜택"
        ],
        "할인율(%)": [10, 5, 3, 4]
    }
    card_df = pd.DataFrame(data)

    def highlight_first_column(val):
        return 'background-color: #87CEFA'

    styled_df = (
        card_df.style
        .set_properties(**{'text-align': 'center'})
        .applymap(highlight_first_column, subset=['카드사'])
    )

    st.markdown("### 💳 현대자동차 카드사 제휴 혜택 비교")
    st.dataframe(styled_df, hide_index=True)


