import streamlit as st
import pandas as pd

# 데이터 로드
@st.cache_data
def load_car_data():
    return pd.read_csv("data/hyundae_car_list.csv")

# HTML 비교 테이블 생성 함수
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
    filtered_df = df.drop(columns=["img_url"], errors="ignore")  # img_url 제거
    transpose_df = filtered_df.set_index("트림명").T.reset_index()
    transpose_df.columns = ["항목"] + df["트림명"].tolist()
    for _, row in transpose_df.iterrows():
        html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
    html += "</table></div>"
    return html

# Streamlit UI
def detail_ui():
    df = load_car_data()
    if df.empty:
        st.error("차량 데이터를 불러올 수 없습니다.")
        return

    모델들 = df["모델명"].unique()
    비교_대상 = st.session_state.get("비교모델", None)

    for 모델 in 모델들:
        st.subheader(f"📌 {모델}")
        모델_df = df[df["모델명"] == 모델].reset_index(drop=True)

        for i in range(0, len(모델_df), 4):
            row = 모델_df.iloc[i:i+4]
            cols = st.columns(4)

            for col, (_, item) in zip(cols, row.iterrows()):
                with col:
                    st.markdown(
                        f"""
                        <div style="border:1px solid #ddd; border-radius:12px; padding:10px; text-align:center;
                                    box-shadow: 2px 2px 8px rgba(0,0,0,0.06); height: 350px;">
                            <div style="height:180px; display:flex; align-items:center; justify-content:center;">
                                <img src="{item['img_url']}" style="height:140px; max-width:100%; object-fit:contain;" />
                            </div>
                            <div style="margin-top: 10px; font-weight:bold;">{item['트림명']}</div>
                            <div style="color:gray;">{int(item['기본가격']):,}원</div>
                        </div>
                        """, unsafe_allow_html=True
                    )
                    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

            # 한 행 끝나고 상세비교 버튼
        with st.expander(f"{모델} 상세비교"):
            비교_데이터 = df[df["모델명"] == 모델]
            st.markdown(generate_html_table(비교_데이터), unsafe_allow_html=True)
