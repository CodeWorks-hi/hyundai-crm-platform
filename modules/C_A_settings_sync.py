# 설정 및 환경 관리
    # 데이터 동기화 상태 UI



# 설정 및 환경 관리 - 데이터 동기화 상태 UI

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

# 세션 상태 초기화
if 'sync_count' not in st.session_state:
    st.session_state.sync_count = 0
if 'last_sync_time' not in st.session_state:
    st.session_state.last_sync_time = datetime.now().strftime("%Y-%m-%d %H:%M")
if 'sync_log' not in st.session_state:
    today = datetime.today()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
    statuses = [random.choice([1, 1, 1, 0]) for _ in dates]
    st.session_state.sync_log = pd.DataFrame({"날짜": dates, "동기화 여부": statuses})

def sync_ui():
    if 'sync_count' not in st.session_state:
        st.session_state.sync_count = 0
    if 'last_sync_time' not in st.session_state:
        st.session_state.last_sync_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    if 'sync_log' not in st.session_state:
        today = datetime.today()
        dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
        statuses = [random.choice([1, 1, 1, 0]) for _ in dates]
        st.session_state.sync_log = pd.DataFrame({"날짜": dates, "동기화 여부": statuses})

    st.subheader("🔄 데이터 동기화 상태")

    st.info("데이터 동기화 시스템 상태를 확인하고, 오류 로그 및 마지막 동기화 일시를 확인합니다.")

    # 수동 동기화 버튼
    if st.button("🔁 수동 동기화 실행"):
        st.session_state.sync_count += 1
        new_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.session_state.last_sync_time = new_time
        st.session_state.sync_log.loc[len(st.session_state.sync_log)] = [new_time[:10], 1]
        st.toast(f"수동 동기화 실행됨! (총 {st.session_state.sync_count}회)", icon="⏳")

        # 🔄 마지막 동기화 시각 표시 (버튼 실행 후 반영되도록 이 위치로 이동)
        last_sync_time = st.session_state.last_sync_time
        st.write(f"🕒 마지막 동기화 시각: **{last_sync_time}**")
        st.success("✅ 모든 데이터가 정상적으로 동기화되었습니다.")    

    st.markdown("---")

    # 최근 동기화 시각화
    df_status = st.session_state.sync_log.tail(7).reset_index(drop=True)
    st.subheader(" 최근 7일간 동기화 성공 여부")
    fig = px.line(df_status, x="날짜", y="동기화 여부",
                  markers=True,
                  title="일별 동기화 성공 여부 (1=성공, 0=실패)",
                  labels={"동기화 여부": "성공 여부"},
                  color_discrete_sequence=["green"])
    fig.update_yaxes(tickvals=[0, 1], ticktext=["실패", "성공"])
    st.plotly_chart(fig, use_container_width=True)

    # 전체 테이블 보기
    with st.expander(" 🗂 원본 데이터 확인"):
        st.dataframe(st.session_state.sync_log, use_container_width=True)
