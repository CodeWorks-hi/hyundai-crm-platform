import streamlit as st
import pandas as pd
from datetime import datetime

def sales_registration_ui():
    st.markdown("<h2 style='color:#2c3e50;'>🧾 차량 판매 등록</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>고객 및 차량 정보를 입력하여 판매 내역을 등록하세요.</p>", unsafe_allow_html=True)

    if "직원이름" not in st.session_state or st.session_state["직원이름"] == "":
        st.warning("딜러 정보를 먼저 등록하세요.")
        return
    if "ordered_model" not in st.session_state:
        st.session_state["ordered_model"] = ""
    if "ordered_trim" not in st.session_state:
        st.session_state["ordered_trim"] = ""
    if "ordered_factory" not in st.session_state:
        st.session_state["ordered_factory"] = ""

    # Load car list dataset
    car_df = pd.read_csv("data/hyundae_car_list.csv")
    car_df = car_df.loc[car_df["브랜드"] != "기아", :]
    plant_df = pd.read_csv("data/inventory_data.csv")
    customers_df = pd.read_csv('data/customers.csv')
    sales_df = pd.read_csv('data/domestic_customer_data.csv')
    plant_df.columns = plant_df.columns.str.strip()
    plant_df = plant_df[plant_df["생산상태"] == "생산중"]

    model_options = sorted(car_df["모델명"].dropna().unique())

    # 판매 등록 입력 폼
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.markdown("##### 🚗 차량 선택")

        selected_model = st.selectbox("차종", model_options)
        available_trims = car_df[car_df["모델명"] == selected_model]["트림명"].dropna().unique()
        selected_trim = st.selectbox("트림명", sorted(available_trims), key=f"trim_{selected_model}")

        filtered_factories = plant_df[
            (plant_df["모델명"] == selected_model) &
            (plant_df["트림명"] == selected_trim)
        ]["공장명"].dropna().unique()
        selected_factory = st.selectbox("공장명", sorted(filtered_factories))

        dealer = st.selectbox("직원명", [st.session_state["직원이름"]], disabled=True)

    with right_col:
        st.markdown("##### 📝 판매 정보")

        stock_qty = plant_df[
            (plant_df["모델명"] == selected_model) &
            (plant_df["트림명"] == selected_trim) &
            (plant_df["공장명"] == selected_factory)
        ]["재고량"].min()

        customer = st.text_input("👤 고객명")
        contact = st.text_input("📞 연락처")
        customer_data = customers_df[(customers_df['상담자명'] == customer) & (customers_df['연락처'] == contact)]
        if customer_data.empty:
            st.markdown("""
                <div style='margin-top: 10px; padding: 12px; background-color: #fff3f3;
                            border-left: 6px solid #e74c3c; border-radius: 6px; color: #b94a48;'>
                    ❌ <strong>해당 고객 정보가 존재하지 않습니다.</strong><br>
                </div>
            """, unsafe_allow_html=True)
            st.write(" ")
        else:
            st.markdown(f"""
                <div style='background-color:#f0f8ff; padding: 10px; border-left: 4px solid #1890ff; border-radius: 5px; margin-bottom: 10px;'>
                    👤 <b>{customer_data.iloc[0]["상담자명"]}</b> / {customer_data.iloc[0]["연락처"]} / {st.session_state["ordered_model"]} {st.session_state["ordered_trim"]} / {st.session_state["ordered_factory"]}
                </div>
            """, unsafe_allow_html=True)

        sale_date = st.date_input("📅 판매일자", value=datetime.today())

        if st.button("✅ 판매 등록"):
            goal_df = pd.read_csv("data/employee_goal.csv")
            goal_df = goal_df[goal_df["직원명"] == dealer]
            
            goal_df[["주간실적", "월간실적", "연간실적"]] += 1
            goal_df.to_csv("data/employee_goal.csv", index=False)

            if customer_data.empty or not contact:
                st.warning("⚠️ 고객명과 연락처를 입력해주세요.")
            elif stock_qty is None or stock_qty < 1 or selected_factory is None:
                st.error("🚫 해당 차량의 재고가 부족합니다.")
            else:
                if len(customer) >= 2:
                    masked_customer = customer[0] + "*" + customer[2:]
                else:
                    masked_customer = customer

                # 기존 구매 횟수 확인
                try:
                    existing_sales_df = pd.read_csv("data/domestic_customer_data.csv")
                    prior_sales_count = existing_sales_df[
                        existing_sales_df["이름"] == customer_data.iloc[0]["상담자명"]
                    ].shape[0]
                    purchase_count = prior_sales_count + 1
                except FileNotFoundError:
                    purchase_count = 1

                new_sale = {
                    "차종": selected_model,
                    "트림명": selected_trim,
                    "공장명": selected_factory,
                    "고객명": masked_customer,
                    "수량": 1,
                    "판매일자": sale_date.strftime("%Y-%m-%d"),
                }

                if "sales_log" not in st.session_state:
                    st.session_state.sales_log = []
                st.session_state.sales_log.append(new_sale)

                # 판매 고객 정보 및 차량 스펙 저장용 항목 구성
                car_info = car_df[
                    (car_df["모델명"] == selected_model) &
                    (car_df["트림명"] == selected_trim)
                ].iloc[0]

                customer_record = {
                    "이름": customer_data.iloc[0]["상담자명"],
                    "연락처": customer_data.iloc[0]["연락처"],
                    "성별": customer_data.iloc[0]["성별"],
                    "현재 나이": datetime.today().year - pd.to_datetime(customer_data.iloc[0]["생년월일"]).year,
                    "구매연도": sale_date.year,
                    "연령대": customer_data.iloc[0]["연령대"],
                    "거주 지역": customer_data.iloc[0]["거주지역"],
                    "차량 구매 횟수": purchase_count,
                    "고객 평생 가치": st.session_state.get("LTV", 0),
                    "브랜드": car_info["브랜드"],
                    "모델명": car_info["모델명"],
                    "기본가격": car_info["기본가격"],
                    "공장명": selected_factory
                }

                # 파일에 누적 저장
                csv_path = "data/domestic_customer_data.csv"
                try:
                    existing_df = pd.read_csv(csv_path)
                    updated_df = pd.concat([existing_df, pd.DataFrame([customer_record])], ignore_index=True)
                except FileNotFoundError:
                    updated_df = pd.DataFrame([customer_record])

                updated_df.to_csv(csv_path, index=False)

                st.success("✅ 판매 등록이 완료되었습니다.")

    # 현재 직원 판매 실적 표시
    goal_df = pd.read_csv("data/employee_goal.csv")
    goal_row = goal_df[goal_df["직원명"] == st.session_state["직원이름"]]

    if not goal_row.empty:
        st.markdown(f"<h4 style='color:#1f77b4;'>📋 {st.session_state['직원이름']} 매니저님의 판매 실적 현황</h4>", unsafe_allow_html=True)
        weekly = int(goal_row["주간실적"].values[0])
        monthly = int(goal_row["월간실적"].values[0])
        yearly = int(goal_row["연간실적"].values[0])

        st.markdown(f"""
            <div style='padding: 10px 15px; background-color: #f6fbff; border-left: 5px solid #1f77b4; border-radius: 6px; margin-bottom: 20px;'>
                <p style='margin: 4px 0;'>📆 <b>주간 실적:</b> {weekly}건</p>
                <p style='margin: 4px 0;'>🗓️ <b>월간 실적:</b> {monthly}건</p>
                <p style='margin: 4px 0;'>📅 <b>연간 실적:</b> {yearly}건</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 누적 판매 통계
    if "sales_log" in st.session_state and st.session_state.sales_log:
        st.markdown("<h4 style='color:#1f77b4;'>📈 누적 판매량 (차종 기준)</h4>", unsafe_allow_html=True)
        df = pd.DataFrame(st.session_state.sales_log)
        stat_df = df.groupby(["차종", "트림명"])["수량"].sum().reset_index().sort_values(by="수량", ascending=False)
        st.dataframe(stat_df.rename(columns={"차종": "차종명", "수량": "누적 판매량"}), use_container_width=True, hide_index=True)

        st.markdown("<h4 style='color:#1f77b4;'>📊 최근 판매 현황</h4>", unsafe_allow_html=True)
        df = df.sort_values(by="판매일자", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("아직 등록된 판매 이력이 없습니다.")