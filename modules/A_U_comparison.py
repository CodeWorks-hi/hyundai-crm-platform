# 고객 메인 대시보드     
    # 차량 비교

import streamlit as st
import pandas as pd
import os

# 데이터 로드 
@st.cache_data
def load_car_data():
    df_path = "data/hyundae_car_list.csv"
    if os.path.exists(df_path):
        return pd.read_csv(df_path)
    else:
        return pd.DataFrame()

# 로드 된 데이터를 저장 
df = load_car_data()

# ▶HTML 테이블 생성 함수 (재사용)
def generate_html_table(df: pd.DataFrame) -> str:
    html = """
    <style>
    .compare-table { width: 100%; border-collapse: collapse; font-size: 14px; table-layout: fixed; }
    .compare-table th, .compare-table td { border: 1px solid #ddd; padding: 8px; text-align: center; word-wrap: break-word; }
    .compare-table th { background-color: #f5f5f5; font-weight: bold; }
    .scroll-wrapper { max-height: 500px; overflow-y: auto; border: 1px solid #ccc; margin-top: 10px; }
    </style>
    <div class="scroll-wrapper">
    <table class="compare-table">
    """
    headers = ["항목"] + df["트림명"].tolist()
    html += "<tr>" + "".join(f"<th>{col}</th>" for col in headers) + "</tr>"
    transpose_df = df.set_index("트림명").T.reset_index()
    transpose_df.columns = ["항목"] + df["트림명"].tolist()
    for _, row in transpose_df.iterrows():
        html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
    html += "</table></div>"
    return html


def comparison_ui():
    st.subheader("🚗 차량 비교")

    df = load_car_data()
    if df.empty:
        st.error("차량 데이터를 불러올 수 없습니다.")
        return

    col2, col3 = st.columns([3, 1])

    with col2:
        st.markdown("### 전체 차량 목록")
        for i in range(0, len(df), 3):
            row = df.iloc[i:i+3]
            cols = st.columns(3)
            for col, (_, item) in zip(cols, row.iterrows()):
                with col:
                    st.image(item["img_url"], width=260)
                    st.markdown(f"**{item['모델명']}** {item['트림명']}")
                    st.markdown(f"{item['기본가격']:,}원")
                    if st.button("이 차량 선택", key=f"선택_{item['모델명']}_{item['트림명']}"):
                        st.session_state["선택차량"] = item.to_dict()
                        st.rerun()

        with st.expander("📋 전체 차량 비교"):
            compare = df.drop(columns=["img_url"]).reset_index(drop=True)
            st.dataframe(compare)

    with col3:
        st.markdown("### 차량 정보")
        if "선택차량" in st.session_state:
            car = st.session_state["선택차량"]
            st.image(car["img_url"], width=200)
            st.markdown(f"**{car['모델명']} {car['트림명']}**")
            st.markdown(f"가격: {car['기본가격']:,}원")

            if st.button("판매 등록으로 이동"):
                st.session_state.current_page = "판매 등록"
                st.rerun()

            st.markdown("---")
            st.markdown("**세부 정보**")
            for col in ['연료구분', '배기량', '공차중량(kg)', '연비', '차량형태', '차량구분']:
                value = car.get(col)
                if pd.notna(value):
                    st.markdown(f"- {col}: {value}")
        else:
            st.info("선택된 차량이 없습니다.")
    

