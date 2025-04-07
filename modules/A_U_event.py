import pandas as pd  # 예: 이벤트 로그 저장 시
import datetime       # 예: 이벤트 시작일/종료일 표시 시
import streamlit as st
import math
import os

def event_ui():
    # 상단 배너 스타일
    st.markdown("""
        <div style="background-color: #f4f0ec; padding: 60px 0; text-align: center;">
            <h1 style="font-size: 48px; font-weight: bold; margin-bottom: 12px;">이벤트</h1>
            <p style="font-size: 18px;">고객님을 위한 스페셜 이벤트는 계속됩니다. 즐거운 행운과 경품을 만나보세요!</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("")
    st.markdown("---")

    # CSV 연동: 진행 중 이벤트만 표시 (카드 형식으로 렌더링)
    csv_path = "data/campaign_list.csv"
    today = datetime.date.today()

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df["시작일"] = pd.to_datetime(df["기간"].str.split("~").str[0].str.strip(), errors="coerce").dt.date
        df["종료일"] = pd.to_datetime(df["기간"].str.split("~").str[1].str.strip(), errors="coerce").dt.date

        진행중 = df[(df["시작일"] <= today) & (df["종료일"] >= today)]

        if not 진행중.empty:

            rows = 진행중.reset_index(drop=True)

            # 상단 2개
            if len(rows) >= 1:
                top_chunk = rows.iloc[:2]
                top_cols = st.columns([0.1, 1, 0.1, 1, 0.1]) if len(top_chunk) == 2 else st.columns([0.1, 1, 0.1, 1e-6, 0.1])
                for col, (_, row) in zip([top_cols[1], top_cols[3]], top_chunk.iterrows()):
                    with col:
                        if pd.notna(row.get("이미지", "")) and os.path.exists(row["이미지"]):
                            st.image(row["이미지"], use_container_width=True)
                        st.markdown(f"#### {row['이벤트명']}")
                        st.caption(row['혜택'])
                        with st.expander("이벤트 - 상세보기"):
                            st.markdown(f"""
                            - **대상**: {row['대상']}  
                            - **혜택**: {row['혜택']}  
                            - **참여 방법**: {row['참여 방법']}  
                            - **기간**: {row['기간']}  
                            - **전략 분류**: {row['분류']}
                            """)

            # 하단 3개씩 반복 출력
            if len(rows) > 2:
                bottom_chunk = rows.iloc[2:]
                for i in range(0, len(bottom_chunk), 3):
                    chunk = bottom_chunk.iloc[i:i+3]
                    cols = st.columns([0.05, 1, 0.05, 1, 0.05, 1, 0.05]) if len(chunk) == 3 else st.columns([0.1, 1, 0.1, 1, 0.1])
                    col_indices = [1, 3, 5] if len(chunk) == 3 else [1, 3]

                    for col, (_, row) in zip([cols[i] for i in col_indices], chunk.iterrows()):
                        with col:
                            if pd.notna(row.get("이미지", "")) and os.path.exists(row["이미지"]):
                                st.image(row["이미지"], use_container_width=True)
                            st.markdown(f"#### {row['이벤트명']}")
                            st.caption(row['혜택'])
                            with st.expander("이벤트 - 상세보기"):
                                st.markdown(f"""
                                - **대상**: {row['대상']}  
                                - **혜택**: {row['혜택']}  
                                - **참여 방법**: {row['참여 방법']}  
                                - **기간**: {row['기간']}  
                                - **전략 분류**: {row['분류']}
                                """)
        else:
            st.info("현재 진행 중인 이벤트가 없습니다.")