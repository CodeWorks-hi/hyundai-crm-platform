import streamlit as st
import pandas as pd
import plotly.express as px


def inventory_ui():
    # 데이터 불러오기 예시
    stock_df = pd.DataFrame({
        "차종": ["Avante", "Sonata", "Grandeur", "Tucson", "Palisade", "Kona"],
        "재고수량": [12, 5, 3, 9, 2, 7]
    })

    sales_df = pd.DataFrame({
        "차종": ["Avante", "Sonata", "Grandeur", "Tucson", "Palisade", "Kona", "Avante", "Kona", "Tucson", "Sonata"],
        "판매량": [20, 15, 8, 13, 6, 11, 18, 9, 12, 14]
    })

    col1, col2 = st.columns([1, 1.3])

    with col1:
        st.subheader("🚗 실시간 재고량 확인")
        st.warning("##### * 현재 보유 중인 차종별 실시간 재고 현황입니다. 이 부분은 실시간 업데이트 가능하도록 코드 수정 필요")
        st.dataframe(stock_df[["차종", "재고수량"]].sort_values(by="재고수량", ascending=False), use_container_width=True)

        st.warning("##### * 차량 판매 데이터 기반으로 재고량과 비교해 판매 양상 확인")
        st.warning("##### * 재고 과잉/부족 차트로 바꾸는 게 나을 수도.")

        colA, colB = st.columns([1, 1.1])

        with colA:
            st.subheader("🔥 최근 판매량 Top 3")
            top3 = sales_df.groupby("차종")["판매량"].sum().sort_values(ascending=False).head(3).reset_index()
            fig_top3 = px.bar(top3, x="차종", y="판매량", title="Top 3 인기 차종")
            st.plotly_chart(fig_top3, use_container_width=True)

        with colB:
            st.subheader("🥶 최근 판매량 Bottom 3")
            bottom3 = sales_df.groupby("차종")["판매량"].sum().sort_values().head(3).reset_index()
            fig_bottom3 = px.bar(bottom3, x="차종", y="판매량", title="판매 부진 차종")
            st.plotly_chart(fig_bottom3, use_container_width=True)
    with col2:
        # 재고 기반 발주 추천
        st.warning("##### * 현재는 재고와 단순 판매량 기준으로 발주 여부 결정 및 추천하는 시스템")
        st.warning("##### * 모델 사용하면 더욱 효과적인 추천 가능할 듯")
        st.markdown("#### 📦 발주 추천")
        merged_df = pd.merge(stock_df, sales_df.groupby("차종")["판매량"].sum().reset_index(), on="차종", how="left").fillna(0)
        merged_df["판매재고비"] = merged_df["판매량"] / (merged_df["재고수량"] + 1)
        reorder_recommend = merged_df.sort_values(by="판매재고비", ascending=False).head(3)

        for _, row in reorder_recommend.iterrows():
            st.info(f"📌 `{row['차종']}`: 재고 {int(row['재고수량'])}대 / 최근 판매량 {int(row['판매량'])}대 ➜ 추가 발주 권장")

        st.markdown("---")
        st.subheader("📋 발주 등록")
        with st.form("order_form"):
            vehicle = st.selectbox("차종 선택", stock_df["차종"].unique())
            size = st.selectbox("사이즈", ["소형", "중형", "대형"])
            color = st.selectbox("색상", ["흰색", "검정", "회색", "파랑", "빨강"])
            quantity = st.number_input("수량", min_value=1, step=1)
            submitted = st.form_submit_button("📦 발주 등록")

            if submitted:
                st.success(f"✅ {vehicle}({size}, {color}) {quantity}대 발주 완료되었습니다.")