# 글로벌 재고 최적화, 공급망 관리
# 재고 회전율 경고 시스템
# 재고 회전율이 임계값 이하인 경우 슬랙으로 경고 메시지 전송
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import os

# 경로 설정
INV_PATH = "data/inventory_data.csv"
LIST_PATH = "data/hyundae_car_list.csv"
OUTPUT_PATH = "data/processed/model_trim_capacity.csv"

# 데이터 로드 함수
@st.cache_data
def load_data():
    df_inv = pd.read_csv(INV_PATH)
    df_list = pd.read_csv(LIST_PATH)
    return df_inv, df_list

# 데이터 전처리 함수
def preprocess_data(df):
    plant_location = {
        "울산공장": (35.546, 129.317),
        "아산공장": (36.790, 126.977),
        "전주공장": (35.824, 127.148),
        "앨라배마공장": (32.806, -86.791),
        "중국공장": (39.904, 116.407),
        "인도공장": (12.971, 77.594),
        "체코공장": (49.523, 17.642),
        "튀르키예공장": (40.922, 29.330),
        "브라질공장": (-23.682, -46.875),
        "싱가포르공장": (1.352, 103.819),
        "인도네시아공장": (-6.305, 107.097)
    }

    df[['위도', '경도']] = pd.DataFrame(
        df['공장명'].map(plant_location).tolist(),
        index=df.index
    )

    np.random.seed(23)
    df["월평균입고"] = np.random.randint(50, 500, size=len(df))
    df["월평균출고"] = np.random.randint(30, 400, size=len(df))
    df["재고회전율"] = (df["월평균출고"] / df["재고량"]).replace([np.inf, -np.inf], 0).fillna(0).round(2)

    df['경고등급'] = np.select(
        [
            df['재고회전율'] <= 0.15,
            df['재고회전율'] <= 0.3,
            df['재고회전율'] > 0.3
        ],
        ['🚨 긴급', '⚠️ 주의', '✅ 정상']
    )
    return df

# 슬랙 알림 시스템
def send_slack_alert(df):
    try:
        slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL") or st.secrets.get("SLACK_WEBHOOK_URL")
        
        if not slack_webhook_url:
            raise ValueError("슬랙 웹훅 URL이 설정되지 않았습니다")

        blocks = [{
            "type": "section",
            "text": {"type": "mrkdwn", "text": "🚨 *재고 경고 발생 목록*"}
        }]

        for _, row in df.iterrows():
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"• 공장: `{row['공장명']}`\n"
                        f"• 부품: `{row['부품명']}`\n"
                        f"• 회전율: `{row['재고회전율']:.2f}`\n"
                        f"• 잔여량: `{int(row['재고량'])}개`"
                    )
                }
            })

        response = requests.post(
            slack_webhook_url,
            json={"blocks": blocks},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()
        st.success("✅ 슬랙 알림 전송 성공!")
    except Exception as e:
        st.error(f"❌ 오류 발생: {str(e)}")

# 메인 UI
def warning_ui():
    # 데이터 로드 및 전처리
    df_inv_raw, df_list = load_data()
    df = preprocess_data(df_inv_raw.copy())

    st.header("현대 글로벌 재고 관리 대시보드")
    
    # 대시보드 헤더
    with st.container(border=True):
        cols = st.columns([2, 1, 1, 2])
        cols[0].markdown("##### IGIS 통합 재고 관리 플랫폼 v2.1")
        threshold = cols[1].slider("⚠️ 회전율 경고선", 0.1, 1.0, 0.3, 0.05)
        cols[2].metric("현재 경고율", f"{threshold:.2f}", delta="목표 0.4")
        cols[3].progress(0.75, text="시스템 건강 지수 75%")

    # 실시간 지도 시각화
    with st.expander("공장 위치 현황", expanded=True):
        fig = px.scatter_mapbox(
            df,
            lat='위도',
            lon='경도',
            color='경고등급',
            size='재고량',
            hover_data=['부품명', '재고회전율'],
            color_discrete_map={
                '🚨 긴급': '#FF0000',
                '⚠️ 주의': '#FFA500',
                '✅ 정상': '#00FF00'
            },
            zoom=3,
            height=600
        )
        fig.update_layout(mapbox_style="carto-positron")
        st.plotly_chart(fig, use_container_width=True)

    # 재고 요약 섹션
    st.markdown("---")
    st.subheader("공장별 부품 재고 요약")
    factory_parts = df.groupby(['공장명', '부품명'], as_index=False)['재고량'].sum()
    st.dataframe(factory_parts, use_container_width=True)

    # 위험 알림 섹션
    st.markdown("---")
    st.subheader("재고 위험 알림")
    danger_parts = df[df['재고량'] < 100]
    
    if not danger_parts.empty:
        cols = st.columns([3,1])
        with cols[0]:
            st.error("📉 일부 부품 재고가 임계치 이하입니다.")
            st.dataframe(danger_parts, use_container_width=True)
        with cols[1]:
            fig = px.pie(danger_parts, names='부품명', title="위험 부품 비율")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ 모든 부품 재고가 정상입니다.")

    # 경고 관리 섹션
    st.markdown("---")
    st.header("재고 경고 관리")
    
    col1, col2 = st.columns([3,1])
    with col1:
        selected_factory = st.selectbox("공장 선택", ['전체'] + df['공장명'].unique().tolist())
    with col2:
        selected_grade = st.multiselect("경고 등급", df['경고등급'].unique(), ['🚨 긴급', '⚠️ 주의'])

    filtered_df = df[df['경고등급'].isin(selected_grade)]
    if selected_factory != '전체':
        filtered_df = filtered_df[filtered_df['공장명'] == selected_factory]

    if not filtered_df.empty:
        st.dataframe(
            filtered_df,
            column_config={
                "재고량": st.column_config.ProgressColumn("잔여량", format="%d개", min_value=0, max_value=500),
                "재고회전율": st.column_config.ProgressColumn("회전율", format="%.2f", min_value=0, max_value=1.0)
            },
            height=400,
            use_container_width=True
        )

        selected_models = st.multiselect("슬랙 전송할 모델 선택", filtered_df['모델명'].unique())
        models_to_send = filtered_df[filtered_df['모델명'].isin(selected_models)]

        if st.button("📤 선택 모델 슬랙 전송", type="primary"):
            if not models_to_send.empty:
                send_slack_alert(models_to_send)
                st.toast("IGIS 시스템 알림 전송 완료", icon="✅")
            else:
                st.warning("전송할 모델을 선택해주세요.")
    else:
        st.success("✅ 모든 재고가 안전 수준입니다.", icon="🛡️")
