# 고객 메인 대시보드   
# 이벤트 및 공지사항



import streamlit as st
import pandas as pd
import plotly.express as px


# +---------+
# | 이벤트    |
# +---------+


def event_ui():

    st.subheader("이벤트 및 공지사항")

    st.markdown("#### 최근 공지사항")
    st.info("[공지] 6월부터 캐스퍼 일렉트릭 예약 판매 시작합니다.")
    st.warning("[점검안내] 5월 10일 02:00~05:00 시스템 점검 예정입니다.")

    st.markdown("---")

    st.markdown("#### 현재 진행 중인 이벤트")
    st.success("신규 방문고객 대상 시승 이벤트 - 5월 1일부터 5월 31일까지!")

    if st.button("이벤트 참여하기"):
        with st.form("event_apply_form"):
            st.write("이벤트 응모 정보를 입력해주세요.")
            name = st.text_input("이름")
            phone = st.text_input("연락처 (숫자만 입력)")
            agree = st.checkbox("개인정보 수집에 동의합니다.")

            submitted = st.form_submit_button("제출하기")
            if submitted:
                if name and phone and agree:
                    st.success(f"{name} 님, 이벤트 신청이 완료되었습니다.")
                else:
                    st.warning("모든 항목을 입력하고 동의해 주세요.")

    st.markdown("---")
    st.markdown("#### 나에게 맞는 카드 혜택 추천")

    priority = st.radio("가장 중요한 혜택은?", ["전기차 충전 혜택", "주유비 할인", "포인트 적립", "최대 할부 개월 수"])

    recommendation = {
        "전기차 충전 혜택": "현대카드 - 최대 10% 전기차 충전 할인 혜택",
        "주유비 할인": "현대카드 - 7% 주유비 할인\n우리카드 - 6% 주유비 할인",
        "포인트 적립": "현대카드 - 5% 적립\n우리카드 - 4% 적립",
        "최대 할부 개월 수": "현대카드 / 하나카드 - 최대 60개월 할부",
        "지난 이벤트 참여율 또는 후기 정보 공유": "이벤트 참여율 및 후기 정보는 고객의 신뢰를 높입니다."
    }

    st.info(recommendation[priority])

    with st.expander("카드사 혜택 상세 조건 보기"):
        st.markdown("""
        **조건 예시**

        - 할부 기간: 개인 신용등급 및 카드사 내부 기준에 따라 차등 적용될 수 있음
        - 주유비/충전 할인: 월 최대 2만 원 한도, 일부 제휴 주유소만 적용
        - 포인트 적립: 전월 실적 기준으로 적립률 달라질 수 있음
        - 제휴 프로모션은 차량 모델 및 지역에 따라 달라질 수 있음

        보다 정확한 정보는 각 카드사 홈페이지 또는 대리점을 통해 확인 가능합니다.
        """)

    st.markdown("---")
    st.markdown("모바일 사용자를 위한 안내")

    st.markdown("""
    - 본 페이지는 데스크탑에 최적화되어 있지만,  
      모바일에서도 주요 정보가 잘 보이도록 아래 요소들이 적용되었습니다:

      - 그래프 및 표는 화면 너비에 맞춰 자동 조절됩니다.
      - 표는 좌우로 스크롤 가능하여 모바일 화면에서도 비교가 가능합니다.
      - 텍스트 정보는 한 줄 요약 형태로 간결하게 제공됩니다.

    > *모바일 사용 중 화면이 잘리지 않거나 버튼이 겹칠 경우, 화면을 가로로 돌려서 보시는 것을 권장합니다.*
    """)

    tab1, tab2, tab3 = st.tabs(["현대자동차", "기아", "제네시스"])

    with tab1:
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
            - 현대/롯데/우리/하나카드 제휴  
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

        st.markdown("### 현대자동차 카드사 제휴 혜택 비교")
        st.dataframe(styled_df, hide_index=True)

    with tab2:
        st.info("기아 자동차 제휴 카드 혜택 정보는 준비 중입니다.")

    with tab3:
        st.info("제네시스 제휴 카드 혜택 정보는 준비 중입니다.")

    st.markdown("---")
    st.markdown("이전 이벤트 요약")

    st.markdown("##### 2024년 12월 겨울 프로모션")
    st.markdown("- 총 1,320명 참여")
    st.markdown("- 인기 모델: 캐스퍼, 아이오닉5")
    st.markdown("- 평균 만족도: 4.7 / 5.0")

    st.markdown("##### 고객 후기")
    st.success("“시승 예약하고 다음날 바로 상담까지 진행했어요. 정말 빠르고 편했습니다!”")
    st.success("“카드 혜택 덕분에 전기차 구매 비용을 꽤 줄일 수 있었어요.”")
