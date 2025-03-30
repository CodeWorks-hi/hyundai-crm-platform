# A_auto_mall.py

import streamlit as st
import pandas as pd

df = pd.read_csv("data/casper_final.csv")

def generate_html_table(df: pd.DataFrame) -> str:
    html = """
    <style>
    .compare-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
        table-layout: fixed;
    }
    .compare-table th, .compare-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
        word-wrap: break-word;
    }
    .compare-table th {
        background-color: #f5f5f5;
        font-weight: bold;
    }
    .scroll-wrapper {
        max-height: 500px;
        overflow-y: auto;
        border: 1px solid #ccc;
        margin-top: 10px;
    }
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


def app():
    st.title("딜러가 고객이 왔을때 차량 목록 보여주기, 고객정보입력하기, 차량 선택 해서 판매 할 경우 판매 등록, 상담내용등록, 고객 성향 파악 , 고객에게 맞춤 차량 추천 ")
    st.markdown("오토몰: 고객 응대 화면")
    tabs = st.tabs([
        "차량 추천", 
        "차량 비교", 
        "고객 정보 입력", 
        "판매 등록",
        "AI 수요 예측",
        "고객 맞춤 추천",
        "casper"
    ])


    with tabs[0]:
        st.write("차량 추천 기능 예정. (대시보드 개요)")

    with tabs[1]:
        st.write("차량 비교 기능 예정. (판매 실적 현황)")

    with tabs[2]:
        st.write("고객 정보 입력 예정. (차량 재고 현황)")

    with tabs[3]:
        st.write("00 화면입니다. (생산 계획 관리)")

    with tabs[4]:
        st.write("00 화면입니다. (AI 수요 예측)")

    with tabs[5]:
        st.write("00 화면입니다. (고객 맞춤 추천)")

    with tabs[6]:
        # 데이터 불러오기
        df = pd.read_csv("data/casper_final.csv")

        # 캐스퍼 모델 분리
        casper = df[df["차종"].str.contains("캐스퍼", na=False) & ~df["차종"].str.contains("일렉트", na=False)]
        electric = df[df["차종"].str.contains("일렉트", na=False)]
        col1, col2, col3 = st.columns([1,3,1])
        with col1:
            pass
        # 캐스퍼 카드 출력
        with col2:
            
            st.markdown("### 캐스퍼 ")
            for i in range(0, len(casper), 3):
                row = casper.iloc[i:i+3]
                cols = st.columns(3)
                for col, (_, item) in zip(cols, row.iterrows()):
                        with col:
                            st.image(item["img_url"], width=260)
                            st.markdown(f"**{item['차종']}**")
                            st.markdown(f"트림: {item['트림명']}")
                            st.markdown(f"가격: {item['기본가격(원)']:,}원")

                # 캐스퍼 비교 테이블
                with st.expander("캐스퍼 비교하기"):
                    casper_compare = casper.drop(columns=["img_url"]).reset_index(drop=True)
                    casper_html = generate_html_table(casper_compare.fillna(""))
                    st.markdown(casper_html, unsafe_allow_html=True)

                # 일렉트릭 카드 출력
                st.markdown("### 캐스퍼 일렉트릭")
                for i in range(0, len(electric), 3):
                    row = electric.iloc[i:i+3]
                    cols = st.columns(3)
                    for col, (_, item) in zip(cols, row.iterrows()):
                        with col:
                            st.image(item["img_url"], width=260)
                            st.markdown(f"**{item['차종']}**")
                            st.markdown(f"트림: {item['트림명']}")
                            st.markdown(f"가격: {item['기본가격(원)']:,}원")

                # 일렉트릭 비교 테이블
                with st.expander("캐스퍼 일렉트릭 비교하기"):
                    electric_compare = electric.drop(columns=["img_url"]).reset_index(drop=True)
                    electric_html = generate_html_table(electric_compare.fillna(""))
                    st.markdown(electric_html, unsafe_allow_html=True)
        with col3:
            pass
            
        if st.button("← 메인으로 돌아가기"):
            st.session_state.current_page = "home"
            st.rerun()
