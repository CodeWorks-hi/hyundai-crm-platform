# 고객 메인 대시보드    
    # 캐스퍼 비교 및 선택

# 고객 메인 대시보드 - 캐스퍼 비교 및 선택
import streamlit as st
import pandas as pd
import os

# ▶️ 캐스퍼 데이터 불러오기
df = pd.read_csv("data/car_type.csv")

@st.cache_data
def load_car_data():
    df_path = "data/car_type.csv"
    if os.path.exists(df_path):
        return pd.read_csv(df_path)
    else:
        return pd.DataFrame()

# ▶️ HTML 테이블 생성 함수 (재사용)
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

# ▶️ 캐스퍼 페이지 렌더링

def casper_ui():
    df = load_car_data()

    if df.empty:
        st.error("차량 데이터를 불러올 수 없습니다.")
        return
    
    # 모델 분리
    casper = df[df["차종"].str.contains("캐스퍼", na=False) & ~df["차종"].str.contains("일렉트", na=False)]
    electric = df[df["차종"].str.contains("일렉트", na=False)]

    col2, col3 = st.columns([3, 1])

    # ✅ 캐스퍼 카드 출력
    with col2:
        st.markdown("### 캐스퍼")
        for i in range(0, len(casper), 3):
            row = casper.iloc[i:i+3]
            cols = st.columns(3)
            for col, (_, item) in zip(cols, row.iterrows()):
                with col:
                    st.image(item["img_url"], width=260)
                    st.markdown(f"**{item['차종']}** {item['트림명']}")
                    st.markdown(f"{item['기본가격(원)']:,}원")
                    if st.button("이 차량 선택", key=f"선택_{item['트림명']}"):
                        st.session_state["선택차량"] = item.to_dict()
                        st.rerun()

        with st.expander("캐스퍼 비교하기"):
            casper_compare = casper.drop(columns=["img_url"]).reset_index(drop=True)
            st.markdown(generate_html_table(casper_compare.fillna("")), unsafe_allow_html=True)

        st.markdown("### 캐스퍼 일렉트릭")
        for i in range(0, len(electric), 3):
            row = electric.iloc[i:i+3]
            cols = st.columns(3)
            for col, (_, item) in zip(cols, row.iterrows()):
                with col:
                    st.image(item["img_url"], width=260)
                    st.markdown(f"**{item['차종']}** {item['트림명']}")
                    st.markdown(f"{item['기본가격(원)']:,}원")
                    if st.button("이 차량 선택", key=f"선택_{item['트림명']}_elec"):
                        st.session_state["선택차량"] = item.to_dict()
                        st.rerun()

        with st.expander("캐스퍼 일렉트릭 비교하기"):
            electric_compare = electric.drop(columns=["img_url"]).reset_index(drop=True)
            st.markdown(generate_html_table(electric_compare.fillna("")), unsafe_allow_html=True)

    # ✅ 선택 차량 정보 출력
    with col3:
        st.markdown("### 차량 정보")
        if "선택차량" in st.session_state:
            car = st.session_state["선택차량"]
            st.image(car["img_url"], width=200)
            st.markdown(f"**{car['차종']} {car['트림명']}**")
            st.markdown(f"가격: {car['기본가격(원)']:,}원")

            if st.button("판매 등록으로 이동"):
                st.session_state.current_page = "판매 등록"
                st.rerun()

            st.markdown("---")
            st.markdown("**세부 정보**")
            for col in ['연료', '배기량(cc)', '최고출력(PS)', '공차중량(kg)', '전비_복합(km/kWh)', '주행거리_복합(km)']:
                value = car.get(col)
                if pd.notna(value):
                    st.markdown(f"- {col}: {value}")
        else:
            st.info("선택된 차량이 없습니다.")