import streamlit as st
import pandas as pd
import plotly.express as px


def inventory_ui():
    # 데이터 불러오기 예시
    inv_df = pd.read_csv("data/inventory_data.csv")
    stock_df = inv_df.groupby(['모델명', '공장명'], as_index=False)['재고량'].sum().rename(columns={'모델명': '차종', '재고량': '재고수량'})
    sal_df = pd.read_csv("data/processed/total/hyundai-by-car.csv")
    
    # 최근 3개월 컬럼만 추출
    recent_cols = sorted([col for col in sal_df.columns if col[:4].isdigit()], reverse=True)[:3]
    sal_df["최근 3개월 판매량"] = sal_df[recent_cols].sum(axis=1)

    # -------------------------------
    # 상단: 컬럼1 (카드뷰) / 컬럼2 (재고 그래프) / 컬럼3 (추천 차량 재고 현황)
    col1, col2, col3 = st.columns([3, 0.3, 1.4])

    with col1:
        colA, colB = st.columns([1, 1.1])

        with colA:
            top3 = sal_df.groupby("차종")["최근 3개월 판매량"].sum().sort_values(ascending=False).head(3).reset_index()
            fig_top3 = px.bar(top3, x="차종", y="최근 3개월 판매량", title="Top 3 인기 차종")
            st.plotly_chart(fig_top3, use_container_width=True)

        with colB:
            bottom3 = sal_df.groupby("차종")["최근 3개월 판매량"].sum().sort_values().head(3).reset_index()
            fig_bottom3 = px.bar(bottom3, x="차종", y="최근 3개월 판매량", title="판매 부진 차종")
            st.plotly_chart(fig_bottom3, use_container_width=True)
        top3_df = stock_df.merge(sal_df, on="차종").sort_values(by="최근 3개월 판매량", ascending=False).head(3).reset_index(drop=True)
        top3_df.index = [""] * len(top3_df)  # 👉 인덱스를 공백으로 덮어서 숨김 효과
        st.dataframe(top3_df, use_container_width=True)

    with col3:
        st.markdown("### 📦 공장별 주요 재고 현황")

        shown_models = set()
        saved_models = [st.session_state.get(f"saved_recommend_{i}") for i in range(1, 4)]
        saved_models = list(filter(None, saved_models))  # Remove None
        saved_models = list(dict.fromkeys(saved_models))  # Preserve order, remove duplicates

        if saved_models:
            for model in saved_models:
                if model in shown_models:
                    continue
                shown_models.add(model)
                match = stock_df[stock_df["차종"] == model]

                if not match.empty:
                    # 가까운 공장 순서 (임의 기준: 이름순)
                    match = match.sort_values(by="공장명").head(3)
                    for _, row in match.iterrows():
                        st.markdown(f"""
                            <div style="border:1px solid #ccc; border-radius:12px; padding:10px; margin-bottom:10px;
                                        background-color:#f9f9f9;">
                                <strong>{row['차종']} @ {row['공장명']}</strong><br>
                                현재 재고: <strong>{int(row['재고수량'])}대</strong>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"'{model}'에 대한 재고 정보 없음")
        else:
            sample_df = stock_df[stock_df["공장명"].str.contains("한국|코리아|Korea", case=False, na=False)]
            sample_df = sample_df.sample(min(6, len(sample_df)), random_state=42)
            for _, row in sample_df.iterrows():
                st.markdown(f"""
                    <div style="border:1px solid #ccc; border-radius:12px; padding:10px; margin-bottom:10px;
                                background-color:#f9f9f9;">
                        <strong>{row['차종']} @ {row['공장명']}</strong><br>
                        현재 재고: <strong>{int(row['재고수량'])}대</strong>
                    </div>
                """, unsafe_allow_html=True)

    # -------------------------------
    # 하단: 컬럼3 (발주 추천) / 컬럼M (발주 등록) / 컬럼4 (발주 등록)
    st.markdown("---")
    col3, col3M, colM, col4M, col4 = st.columns([1.3, 0.1, 1.3, 0.1, 1.5])

    with col3:
        st.markdown("### 🏭 재고 부족 알림 (공장 기준)")

        # 재고량 기준으로 공장+차종별 top 3 적은 항목 추출
        low_inventory_df = (
            inv_df.groupby(['공장명', '모델명'], as_index=False)['재고량']
            .sum()
            .rename(columns={'모델명': '차종', '재고량': '재고수량'})
            .sort_values(by='재고수량', ascending=True)
            .head(3)
        )

        # 카드 스타일 출력
        st.markdown("""
            <style>
            .scroll-container {
                max-height: 500px;
                overflow-y: auto;
                padding-right: 8px;
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
        for _, row in low_inventory_df.iterrows():
            st.markdown(f"""
                <div class="inventory-card">
                    <h4>{row['차종']}</h4>
                    <p>공장: <strong>{row['공장명']}</strong></p>
                    <p>현재 재고: <strong>{int(row['재고수량'])}대</strong></p>
                    <p style="color:#d9534f;"><strong>⚠️ 재고 부족 주의</strong></p>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with colM:
        st.markdown("### 발주 추천")
        st.markdown("###### ")

        merged_df = pd.merge(
            stock_df,
            sal_df.groupby("차종")["최근 3개월 판매량"].sum().reset_index(),
            on="차종",
            how="left"
        ).fillna(0)

        merged_df["판매재고비"] = merged_df["최근 3개월 판매량"] / (merged_df["재고수량"] + 1)
        reorder_recommend = merged_df.sort_values(by="판매재고비", ascending=False).head(3)

        # 카드뷰 형태 출력
        for _, row in reorder_recommend.iterrows():
            st.markdown(f"""
                <div style="border:1px solid #ccc; border-radius:12px; padding:14px; margin-bottom:12px;
                            box-shadow:2px 2px 6px rgba(0,0,0,0.05); text-align:center;">
                    <h4>{row['차종']}</h4>
                    <p>재고: <strong>{int(row['재고수량'])}대</strong></p>
                    <p>판매: <strong>{int(row['최근 3개월 판매량'])}대</strong></p>
                    <p style="color:#d9534f;"><strong>➜ 추가 발주 권장</strong></p>
                </div>
            """, unsafe_allow_html=True)

    with col4:
        st.markdown("### 발주 등록")
        st.caption("필요한 차량을 선택해 발주를 등록하세요.")

        with st.form("order_form_col4"):  # ✅ 키를 유니크하게 변경
            st.markdown(
                """
                <div style="border:1px solid #e1e1e1; border-radius:12px; padding:20px; background-color:#fafafa;">
                """,
                unsafe_allow_html=True,
            )

            vehicle = st.selectbox("차종 선택", stock_df["차종"].unique())
            size = st.radio("사이즈", ["소형", "중형", "대형"], horizontal=True)
            color = st.selectbox("색상", ["흰색", "검정", "회색", "파랑", "빨강"])
            quantity = st.number_input("수량", min_value=1, step=1)

            submitted = st.form_submit_button("발주 등록")

            st.markdown("</div>", unsafe_allow_html=True)

            if submitted:
                st.success(f"`{vehicle}` ({size}, {color}) {quantity}대 발주 완료되었습니다.")


    # -------------------------------
    # 전체 테이블 익스펜더
    with st.expander("전체 재고 테이블 보기"):
        st.dataframe(stock_df.pivot_table(index="차종", columns="공장명", values="재고수량", fill_value=0))