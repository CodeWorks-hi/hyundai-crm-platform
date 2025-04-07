import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime

def inventory_ui():
    if "직원이름" not in st.session_state or st.session_state["직원이름"] == "":
        st.warning("딜러 정보를 먼저 등록하세요.")
        return

    # 데이터 불러오기 예시
    inv_df = pd.read_csv("data/inventory_data.csv")
    inv_df = inv_df.loc[inv_df["브랜드"] != "기아", :]
    delay_reason_dict = {
        "배터리팩": "해외 공급망 이슈로 인한 지연",
        "엔진": "공장 생산 설비 점검 중",
        "와이퍼 모터": "부품 수입 통관 지연",
        "에어백 모듈": "품질 검수로 인한 납기 지연",
        "변속기": "일시적 수요 폭증",
        "LED 헤드램프": "국내 공급사 생산 차질",
        "타이어": "물류센터 이송 지연",
        "제동 시스템": "부품 리콜 대응 조정",
        "서스펜션": "국내 공급 계약 해지 여파",
        "기타": "부품 조달 중 예기치 못한 문제",
        "인포테인먼트 유닛": "소프트웨어 호환성 문제로 공급 지연",
        "히터 코어": "겨울철 수요 급증으로 인한 부족",
        "스티어링 휠": "부품 설계 변경으로 인한 생산 중단",
        "연료 펌프": "리콜 대응 재배정 중",
        "냉각팬": "모듈 오류 발생으로 생산 지연",
        "헤드램프": "수입 부품 운송 일정 지연",
        "모터": "모듈 단위 불량 증가로 인한 생산 중단",
        "브레이크 패드": "안전성 인증 대기",
        "배선 하니스": "내부 설계 변경으로 인한 지연",
        "클러치 디스크": "협력사 생산라인 정비로 납기 지연"
    }
    inv_df["차종"] = inv_df["모델명"].astype(str) + " " + inv_df["트림명"].astype(str)
    stock_df = inv_df.groupby(['차종', '공장명'], as_index=False)['재고량'].sum().rename(columns={'재고량': '생산 가능 수량'})
    sal_df = pd.read_csv("data/processed/total/hyundai-by-car.csv")
    
    # 최근 3개월 컬럼만 추출
    recent_cols = sorted([col for col in sal_df.columns if col[:4].isdigit()], reverse=True)[:3]
    sal_df["최근 3개월 판매량"] = sal_df[recent_cols].sum(axis=1)

    # -------------------------------
    # 상단: 컬럼1 (카드뷰) / 컬럼2 (재고 그래프) / 컬럼3 (추천 차량 재고 현황)
    col1, col2, col3 = st.columns([3, 0.3, 1.4])

    with col1:
        st.markdown("### 📊 최근 3개월 판매량 차트")
        colA, colB = st.columns([1, 1.1])

        with colA:
            top10 = sal_df.groupby("차종")["최근 3개월 판매량"].sum().sort_values(ascending=False).head(10).reset_index()
            fig_top10 = px.bar(
                top10,
                x="차종",
                y="최근 3개월 판매량",
                title="Top 3 인기 차종 (최근 3개월)",
                color_discrete_sequence=["#E74C3C"]
            )
            st.plotly_chart(fig_top10, use_container_width=True)
            st.markdown(f"""
                <div style="margin-top: 12px; font-size: 0.9rem; background-color: #f8f9fa;
                            border-left: 4px solid #E74C3C; padding: 10px 14px; border-radius: 6px;">
                    <b>상위 판매 차종 분석:</b><br>
                    <u>{top10['차종'].iloc[0]}</u>, <u>{top10['차종'].iloc[1]}</u>, <u>{top10['차종'].iloc[2]}</u> 모델이 최근 3개월 동안 가장 많이 판매되었습니다.
                    해당 차종에 대한 <b>수요 집중 현상</b>이 두드러지며, <b>재고 확보 및 프로모션 강화</b>가 권장됩니다.
                </div>
            """, unsafe_allow_html=True)

        with colB:
            bottom10 = sal_df.groupby("차종")["최근 3개월 판매량"].sum()
            bottom10 = bottom10[bottom10 > 0].sort_values().head(10).reset_index()

            fig_bottom10 = px.bar(
                bottom10,
                x="차종",
                y="최근 3개월 판매량",
                title="판매 저조 Top 3 (최근 3개월, 판매량 0 제외)"
            )
            st.plotly_chart(fig_bottom10, use_container_width=True)
            st.markdown(f"""
                <div style="margin-top: 12px; font-size: 0.9rem; background-color: #fcfcfc;
                            border-left: 4px solid #999; padding: 10px 14px; border-radius: 6px;">
                    <b>판매 저조 차종 분석:</b><br>
                    <u>{bottom10['차종'].iloc[0]}</u>, <u>{bottom10['차종'].iloc[1]}</u>, <u>{bottom10['차종'].iloc[2]}</u> 모델은 판매량이 낮은 차종으로 나타났습니다.
                    <b>공장별 생산 조정</b> 또는 <b>전환 마케팅</b> 전략 검토가 필요합니다.
                </div>
            """, unsafe_allow_html=True)

    with col3:
        st.markdown("### 📦 주요 공장별 생산 가능 수량 현황")

        shown_models = set()
        saved_models = []
        for i in range(1, 4):
            model = st.session_state.get(f"saved_recommend_{i}")
            trim = st.session_state.get(f"saved_recommend_trim_{i}")
            if model and trim:
                full_model = f"{model} {trim}"
                if full_model not in saved_models:
                    saved_models.append(full_model)

        if saved_models:
            for model in saved_models:
                if model in shown_models:
                    continue
                shown_models.add(model)
                split_model = model.split(" ", 1)
                base_model = split_model[0]
                trim_name = split_model[1] if len(split_model) > 1 else ""

                match = inv_df[(inv_df["모델명"] == base_model) & (inv_df["트림명"] == trim_name)]

                if not match.empty:
                    match = (
                        match.groupby(["공장명", "차종"], as_index=False)["재고량"]
                        .min()
                        .rename(columns={"재고량": "생산 가능 수량"})
                    )
                
                if not match.empty:
                    # 가까운 공장 순서 (임의 기준: 이름순)
                    match = match.sort_values(by="공장명").head(2)
                    for _, row in match.iterrows():
                        st.markdown(f"""
                            <div style="border:1px solid #ccc; border-radius:12px; padding:10px; margin-bottom:10px;
                                        background-color:#f9f9f9;">
                                <strong>{row['차종']} @ {row['공장명']}</strong><br>
                                현재 생산 가능 수량: <strong>{int(row['생산 가능 수량'])}대</strong>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"'{model}'에 대한 재고 정보 없음")
        else:
            inv_df["차종"] = inv_df["모델명"].astype(str) + " " + inv_df["트림명"].astype(str)
            sample_df = (
                inv_df.groupby(['공장명', '차종'], as_index=False)['재고량']
                .min()
                .rename(columns={'재고량': '생산 가능 수량'})
                .sample(n=min(6, len(inv_df)), random_state=42)
            )
            for _, row in sample_df.iterrows():
                st.markdown(f"""
                    <div style="border:1px solid #ccc; border-radius:12px; padding:10px; margin-bottom:10px;
                                background-color:#f9f9f9;">
                        <strong>{row['차종']} @ {row['공장명']}</strong><br>
                        현재 생산 가능 수량: <strong>{int(row['생산 가능 수량'])}대</strong>
                    </div>
                """, unsafe_allow_html=True)

    # -------------------------------
    # 하단: 컬럼3 (발주 추천) / 컬럼M (발주 등록) / 컬럼4 (발주 등록)
    st.markdown("---")
    col3, col3M, colM, col4M, col4 = st.columns([1.5, 0.1, 1.5, 0.1, 1.1])

    with col3:
        st.markdown("### 🏭 출고 이슈")
        
        inv_df["차종트림"] = inv_df["모델명"].astype(str) + " " + inv_df["트림명"].astype(str)
        low_inventory_df = (
            inv_df.groupby(['공장명', '차종트림'], as_index=False)['재고량']
            .min()
            .rename(columns={'차종트림': '차종', '재고량': '생산 가능 수량'})
            .sort_values(by='생산 가능 수량', ascending=True)
            .head(3)
        )

        parts_df = inv_df.copy()

        delay_weeks_dict = {
            "배터리팩": 8,
            "엔진": 6,
            "와이퍼 모터": 5,
            "에어백 모듈": 7,
            "변속기": 6,
            "LED 헤드램프": 4,
            "타이어": 3,
            "제동 시스템": 6,
            "서스펜션": 5,
            "기타": 6,
            "인포테인먼트 유닛": 7,
            "히터 코어": 4,
            "스티어링 휠": 5,
            "연료 펌프": 6,
            "냉각팬": 5,
            "헤드램프": 4,
            "모터": 6,
            "브레이크 패드": 5,
            "배선 하니스": 5,
            "클러치 디스크": 6
        }

        # 카드 스타일 출력
        st.markdown("""
            <style>
            .scroll-container {
                max-height: 520px;
                overflow-y: auto;
                padding-right: 8px;
                margin-bottom: 10px;
                scrollbar-width: thin;
            }
            .inventory-card {
                border: 1px solid #ccc;
                border-radius: 12px;
                padding: 14px;
                margin-bottom: 12px;
                text-align: center;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.05);
                background-color: #fff;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
        for i, (_, row) in enumerate(low_inventory_df.iterrows()):
            matched_rows = parts_df[
                (parts_df["공장명"] == row["공장명"]) &
                (parts_df["모델명"] + " " + parts_df["트림명"] == row["차종"])
            ]
            if not matched_rows.empty:
                part_row = matched_rows.loc[matched_rows["재고량"].idxmin()]
                part_name = part_row["부품명"]
                delay_reason = delay_reason_dict.get(part_name, "부품 조달 문제")
                reason = f"{part_name} 부족 - {delay_reason}"
            else:
                reason = "재고 정보 없음"
                
            delay_weeks = delay_weeks_dict.get(part_name, 6)
            st.markdown(f"""
                <div class="inventory-card">
                    <h4>{row['차종']}</h4>
                    <p>공장: <strong>{row['공장명']}</strong></p>
                    <p>생산 가능 수량: <strong>{int(row['생산 가능 수량'])}대</strong></p>
                    <p>출고 지연 이유: <strong>{reason}</strong></p>
                    <p style="color:#d9534f;"><strong>⏱️ 예상 출고 소요 기간: 약 {delay_weeks}주</strong></p>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with colM:
        st.markdown("### 🔍 발주 가능 수량 검색")
        st.markdown("#### 공장을 선택하여 발주 가능 수량을 확인하세요.")
        
        selected_model = st.selectbox("🚗 차종 선택", sorted(inv_df["모델명"].unique()))

        filtered_trims = inv_df[
            (inv_df["모델명"] == selected_model)
        ]["트림명"].unique()
        selected_trim = st.selectbox("🔧 트림명 선택", sorted(filtered_trims))

        result = inv_df[
            (inv_df["모델명"] == selected_model) &
            (inv_df["트림명"] == selected_trim)
        ]
        
        st.markdown("#### 🔎 검색 결과")
        if not result.empty:
            grouped_result = (
                result.groupby(["공장명", "모델명", "트림명"], as_index=False)["재고량"]
                .min()
                .rename(columns={"재고량": "생산 가능 수량"})
            )

            colA, colB, colC = st.columns(3)
            with colA:
                st.metric("공장 수", grouped_result['공장명'].nunique())
            with colB:
                st.metric("총 생산 가능 수량", int(grouped_result["생산 가능 수량"].sum()))
            with colC:
                st.metric("최소 생산 가능 수량", int(grouped_result["생산 가능 수량"].min()))

            st.dataframe(grouped_result[["공장명", "모델명", "트림명", "생산 가능 수량"]].sort_values("생산 가능 수량", ascending=False),
                         use_container_width=True, hide_index=True)
            
        else:
            st.info("선택한 조건에 해당하는 결과가 없습니다.")

    with col4:
        st.markdown("### 📋 발주 등록")
        st.caption("필요한 차량을 선택해 발주를 등록하세요.")

        vehicle_models = sorted(inv_df["모델명"].unique())
        selected_model = st.selectbox("🚗 차종 선택", vehicle_models, key='inven_car')

        available_trims = inv_df[inv_df["모델명"] == selected_model]["트림명"].unique()
        selected_trim = st.selectbox("🔧 트림 선택", sorted(available_trims), key='inven_trim')
        available_factories = inv_df[
            (inv_df["모델명"] == selected_model) &
            (inv_df["트림명"] == selected_trim)
        ]["공장명"].dropna().unique()
        selected_factory = st.selectbox("🏭 공장 선택", sorted(available_factories), key='inven_fac')
        quantity = 1
        client_name = st.text_input("👤 고객명", key="inv_name")
        client_contact = st.text_input("📞 연락처", key="inv_contact")
        requestor = st.text_input("👤 요청자", value=st.session_state.get("manager_name", "홍길동"), disabled=True)

        submitted = st.button("✅ 발주 등록")

        if submitted:
            car_df = pd.read_csv("data/hyundae_car_list.csv")
            car_df = car_df.loc[car_df["브랜드"] != "기아", :]
            sale_date = datetime.today()
            customers_df = pd.read_csv('data/customers.csv')
            customer_data = customers_df[(customers_df['상담자명'] == client_name) & (customers_df['연락처'] == client_contact)]
            
            if customer_data.empty:
                st.markdown("""
                    <div style='margin-top: 10px; padding: 12px; background-color: #fff3f3;
                                border-left: 6px solid #e74c3c; border-radius: 6px; color: #b94a48;'>
                        ❌ <strong>해당 고객 정보가 존재하지 않습니다.</strong><br>
                    </div>
                """, unsafe_allow_html=True)
                st.write(" ")
            else:
                # 기존 구매 횟수 확인
                try:
                    existing_sales_df = pd.read_csv("data/domestic_customer_data.csv")
                    prior_sales_count = existing_sales_df[
                        existing_sales_df["이름"] == customer_data.iloc[0]["상담자명"]
                    ].shape[0]
                    purchase_count = prior_sales_count + 1
                except FileNotFoundError:
                    purchase_count = 1

                # 판매 고객 정보 및 차량 스펙 저장용 항목 구성
                car_match = car_df[
                    (car_df["모델명"] == selected_model) &
                    (car_df["트림명"] == selected_trim)
                ]

                if not car_match.empty:
                    car_info = car_match.iloc[0]
                    # 이후 car_info 사용
                else:
                    st.error("❌ 선택한 차종 및 트림에 해당하는 차량 정보가 존재하지 않습니다.")
                    return

                customer_record = {
                    "이름": customer_data.iloc[0]["상담자명"],
                    "연락처": customer_data.iloc[0]["연락처"],
                    "성별": customer_data.iloc[0]["성별"][0],
                    "현재 나이": datetime.today().year - pd.to_datetime(customer_data.iloc[0]["생년월일"]).year,
                    "구매연도": sale_date.year,
                    "연령대": customer_data.iloc[0]["연령대"],
                    "거주 지역": customer_data.iloc[0]["거주지역"],
                    "차량 구매 횟수": purchase_count,
                    "고객 평생 가치": st.session_state.get("LTV", 0),
                    "브랜드": car_info["브랜드"],
                    "모델명": car_info["모델명"],
                    "트림명": car_info["트림명"],
                    "기본가격": car_info["기본가격"],
                    "공장명": selected_factory,
                    "실구매여부": 0
                }

                # 파일에 누적 저장
                csv_path = "data/domestic_customer_data.csv"
                try:
                    existing_df = pd.read_csv(csv_path)
                    updated_df = pd.concat([existing_df, pd.DataFrame([customer_record])], ignore_index=True)
                except FileNotFoundError:
                    updated_df = pd.DataFrame([customer_record])

                updated_df.to_csv(csv_path, index=False)  

                vehicle = f"{selected_model} {selected_trim}"
            
                # 재고 차감
                inv_df.loc[
                    (inv_df["모델명"] == selected_model) &
                    (inv_df["트림명"] == selected_trim) &
                    (inv_df["공장명"] == selected_factory),
                    ["재고량"]
                ] -= 1

                # 생산 가능 수량은 재계산
                inv_df["차종"] = inv_df["모델명"].astype(str) + " " + inv_df["트림명"].astype(str)
                stock_df = (
                    inv_df.groupby(['차종', '공장명'], as_index=False)['재고량']
                    .min()
                    .rename(columns={'재고량': '생산 가능 수량'})
                )      
                
                # 저장
                inv_df.to_csv("data/inventory_data.csv", index=False)

                st.markdown(f"""
                    <div style="margin-top: 25px; padding: 20px; background-color: #f0f9ff; border-left: 6px solid #1890ff; border-radius: 8px;">
                        <h4 style="color: #1a73e8;">📦 발주 등록 완료</h4>
                        <p style="margin: 6px 0;">차량이 성공적으로 발주되었습니다.</p>
                        <ul style="margin-left: 1rem; padding-left: 0.5rem;">
                            <li><b>차종:</b> {vehicle}</li>
                            <li><b>공장:</b> {selected_factory}</li>
                            <li><b>요청자:</b> {requestor}</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("##### ")

    # -------------------------------
    # 전체 테이블 익스펜더
    with st.expander("🔧 전체 생산 가능 수량 테이블 보기"):
        pivot_df = inv_df.groupby(['차종', '공장명'])['재고량'].min().reset_index()
        pivot_df = pivot_df.rename(columns={"재고량": "생산 가능 수량"})
        st.dataframe(pivot_df.pivot(index="차종", columns="공장명", values="생산 가능 수량").fillna(0).astype(int))

    with st.expander("🗂 원본 데이터 확인", expanded=False):
        tab1, tab2 = st.tabs(["차종별 판매량 통계", "부품 재고 현황"])
        with tab1:
            base_df = pd.read_csv("data/processed/total/hyundai-by-car.csv")
            st.dataframe(base_df, hide_index=True, use_container_width=True)
        with tab2:
            base_df = pd.read_csv("data/inventory_data.csv")
            st.dataframe(base_df, hide_index=True, use_container_width=True)