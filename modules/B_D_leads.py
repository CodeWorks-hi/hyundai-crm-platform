import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import numpy as np


def leads_ui():
    st.markdown("### 👥 고객 리드 관리 대시보드")

    if "직원이름" not in st.session_state or st.session_state["직원이름"] == "":
        st.warning("딜러 정보를 먼저 등록하세요.")
        return
    else:
        dealer_name = st.session_state["직원이름"]
        dealer_id = st.session_state["사번"]
        

    col1, col2, col3 = st.columns([1, 1, 4])
    # with col1:
    #     dealer_name = st.text_input("딜러 성명", key="leads_dealer_name")
    # with col2:
    #     dealer_id = st.text_input("딜러 사번", key="leads_dealer_id")

    if dealer_name == "" or dealer_id == "":
        st.warning("딜러 정보를 먼저 등록하세요.")
        return
    else:
        with col1:
            selected_name = st.text_input("고객 성명 입력", key="leads_name")
        with col2:
            selected_contact = st.text_input("고객 연락처 입력", key="leads_contact")

        df = pd.read_csv("data/customers.csv")

        if df.loc[(df['상담자명'] == selected_name) & (df['연락처'] == selected_contact)].empty:
            st.error('회원 정보가 존재하지 않습니다.')
        else:
            sales_point = 0

            # 이제 고객 정보 (구매 이력, 서비스 이용 내역, 상담 내역 등 횟수) 가져올 것
            sales_df = pd.read_csv("data/domestic_customer_data.csv")
            sales_df = sales_df.loc[(sales_df['이름'] == selected_name) & (sales_df['연락처'] == selected_contact), :]

            sales_cnt = sales_df["차량 구매 횟수"].max()
            if sales_cnt is np.nan:
                sales_cnt = 0
            sales_point += sales_cnt * 30

            sales_amount = sales_df["기본가격"].sum()
            if sales_amount >= 300000000 :
                sales_point += 70
            elif sales_amount >= 200000000 :
                sales_point += 50
            elif sales_amount >= 100000000 :
                sales_point += 40
            elif sales_amount >= 75000000 :
                sales_point += 20
            elif sales_amount >= 50000000 :
                sales_point += 10

            age_group = str(sales_df["연령대"].min())
            if age_group.split(' ')[0] in ["20대", "30대", "40대"]:
                sales_point += 30
            elif age_group.split(' ')[0] in ["10대", "50대"]:
                sales_point += 20
            else:
                sales_point += 10

            # 상담 기록 가져오기
            consult_df = pd.read_csv("data/consult_log.csv")
            consult_df = consult_df.loc[(consult_df["이름"] == selected_name) & (consult_df["전화번호"] == selected_contact), :]
            visit_df = consult_df.loc[consult_df["목적"] == "방문", :]

            consult_cnt = consult_df["상담날짜"].count()
            visit_cnt = visit_df["상담날짜"].count()
            recent_purch = sales_df["구매연도"].max()
            
            grade = 0

            if sales_cnt == 0 and consult_cnt == 0 and visit_cnt == 0:
                grade = 5
            elif sales_cnt == 0 and consult_cnt >= 1 and visit_cnt == 0:
                grade = 4
            elif sales_cnt == 0 and consult_cnt >= 0 and visit_cnt >= 1:
                grade = 3
            elif sales_cnt == 1 and recent_purch >= 2024:
                grade = 2
            else :
                grade = 1
                

            st.markdown(f"""
                <div style="margin: 20px 0; padding: 15px; background-color: #f0f8ff; border-left: 6px solid #1f77b4; border-radius: 6px;">
                    <h4 style="color:#1f77b4; margin: 0;">👤 {selected_name} 고객님은 <span style='color:#e67e22;'>등급 {grade}</span> 고객입니다.</h4>
                </div>
            """, unsafe_allow_html=True)
            st.write(" ")

            grade_descriptions = {
                1: "브랜드에 대한 충성도가 매우 높고, 장기 고객으로 관리가 필요한 핵심 VIP입니다.",
                2: "구매 이력이 있으며, 비교적 최근에 거래가 있었던 충성 잠재 고객입니다.",
                3: "구매 의사는 있으나 아직 충분한 정보 제공 및 설득이 필요한 중간 단계 고객입니다.",
                4: "초기 유입 고객으로, 명확한 니즈 파악과 신뢰 형성이 우선되어야 합니다.",
                5: "브랜드에 대한 인식이 낮거나 첫 상담을 진행 중인 신규 고객입니다."
            }

            followup_checklist = {
                1: ["✔ VIP 감사 혜택 제공", "✔ 신차 출시 시 우선 안내", "✔ 전담 컨설턴트 배정"],
                2: ["✔ 재구매 프로모션 안내", "✔ 모델 업그레이드 제안", "✔ 맞춤 금융 상품 제안"],
                3: ["✔ 다음 방문 시 추가 제품 소개", "✔ 구매 혜택 프로모션 안내", "✔ 시승 예약 유도"],
                4: ["✔ 니즈 파악 상담 예약 권장", "✔ 방문 유도 프로모션 제공", "✔ 초기 관심모델 비교 제공"],
                5: ["✔ 제품 브로셔 및 샘플 제공", "✔ 브랜드 소개 및 첫 방문 유도", "✔ 온라인 상담 연결"]
            }

            # 컬럼 구성
            col1, col2, col3, col4, col5 = st.columns([1.2, 0.1, 2, 0.1, 2])

            with col1:
                progress_ratio = (6 - grade) / 5
                stage_labels = ["유입", "관심/검토", "욕구", "구매/전환", "유지/확산"]

                bar_html = f"""
                <div style='display: flex; align-items: center; height: 220px; background-color: #f9f9f9; border-radius: 8px; padding: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);'>
                    <div style='width: 35px; height: 100%; background-color: #e0e0e0; border-radius: 6px; overflow: hidden; display: flex; flex-direction: column-reverse; position: relative;'>
                        <div style='height: {int(progress_ratio * 100)}%; background: linear-gradient(to top, #1f77b4, #4fa3e3); transition: height 0.5s;'></div>
                    </div>
                    <div style='margin-left: 14px; display: flex; flex-direction: column; justify-content: space-between; height: 100%;'>
                        {''.join([f"<span style='font-size: 0.8rem; color: #333;'>{stage}</span>" for stage in reversed(stage_labels)])}
                    </div>
                </div>
                """
                st.markdown(bar_html, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div style="margin-top: 8px; padding: 4px 10px; background-color: #1f77b4; color: white; border-radius: 20px; display: inline-block; font-weight: bold;">
                        현재 등급: {grade} / 5
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("##### ")

            with col3:
                st.info(f"**등급 {grade}**: \n\n{grade_descriptions.get(grade, '')}")

                st.success(f"✅ 차량 구매: {sales_cnt}회\n\n✅ 상담 내역: {consult_cnt}회\n\n✅ 매장 방문: {visit_cnt}회")

            with col5:  
                st.markdown(f"""
                    <div style="margin-top: 8px;">
                        <strong>누적 충성도 점수: {sales_point}점</strong>
                        <div style="background-color: #eee; border-radius: 8px; height: 18px; margin-top: 5px;">
                            <div style="width: {min(sales_point,100)}%; background: linear-gradient(to right, #1f77b4, #4fa3e3); height: 100%; border-radius: 8px;"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.write(" ")

                with st.expander("📌 고객 맞춤 팔로업 제안 보기", expanded=True):
                    for item in followup_checklist.get(grade, []):
                        st.checkbox(item)

            if not consult_df.empty:
                recent_logs = consult_df.sort_values("상담날짜", ascending=False).head(3)
                st.markdown("### 🗂️ 최근 문의 및 방문 상담 내역")
                for _, row in recent_logs.iterrows():
                    st.markdown(f"""
                        <div style='padding: 10px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 10px; background-color: #fafafa;'>
                            <b>📅 {row['상담날짜']}</b><br>
                            목적: {row['목적']}<br>
                            상담 내용: {row['상담내용']}
                        </div>
                    """, unsafe_allow_html=True)

    st.markdown("###### ")

    with st.expander("🗂 원본 데이터 확인", expanded=False):
        tab1, tab2, tab3 = st.tabs(["고객 설문조사 기록", "차량 판매 기록", "고객 상담 신청 기록"])
        with tab1:
            base_df = pd.read_csv("data/customers.csv")
            st.dataframe(base_df, hide_index=True, use_container_width=True)
        with tab2:
            base_df = pd.read_csv("data/domestic_customer_data.csv")
            st.dataframe(base_df, hide_index=True, use_container_width=True)
        with tab3:
            base_df = pd.read_csv("data/consult_log.csv")
            st.dataframe(base_df, hide_index=True, use_container_width=True)