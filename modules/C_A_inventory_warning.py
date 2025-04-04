
    # 글로벌 재고 최적화, 공급망 관리
        # 재고 회전율 경고 시스템
            # 재고 회전율이 임계값 이하인 경우 슬랙으로 경고 메시지 전송

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests

# 데이터 전처리 함수
def preprocess_data(df):
    # 공장 좌표 정보 추가 (검색 결과 [1] 반영)
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
    
    # 재고 회전율 계산 (검색 결과 [2]의 LTV 모델 반영)
    np.random.seed(23)
    df["월평균입고"] = np.random.randint(50, 500, size=len(df))
    df["월평균출고"] = np.random.randint(30, 400, size=len(df))
    df["재고회전율"] = (df["월평균출고"] / df["재고량"]).replace([np.inf, -np.inf], 0).round(2)
    
    # 3단계 경고 시스템 (검색 결과 [3] 기준)
    df['경고등급'] = np.select(
        [
            df['재고량'] <= 100,
            df['재고량'] <= 200,
            df['재고량'] > 200
        ],
        ['🚨 긴급', '⚠️ 주의', '✅ 정상'],
        default='✅ 정상'
    )
    
    return df

# 슬랙 알림 시스템
def send_slack_alert(df):
    SLACK_WEBHOOK_URL = st.secrets["SLACK_WEBHOOK_URL"]
    
    blocks = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "🚨 *재고 경고 발생*"
        }
    }]
    
    for _, row in df.iterrows():
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"• 공장: {row['공장명']}\n• 부품: {row['부품명']}\n• 회전율: {row['재고회전율']:.2f}\n• 잔여량: {row['재고량']}개"
            }
        })
    
    # Slack webhook
    SLACK_WEBHOOK_URL = st.secrets["SLACK_WEBHOOK_URL"]
    response = requests.post(SLACK_WEBHOOK_URL, json={"blocks": blocks})
    
    if response.status_code != 200:
        st.error("슬랙 알림 전송 실패")
    else:
        st.success("슬랙 알림 전송 성공")

# 메인 UI
def warning_ui():

    
    # 데이터 로드 및 전처리
    inventory_path = "data/inventory_data.csv"
    df = preprocess_data(pd.read_csv(inventory_path))
    
    st.title("🌍 현대기아 글로벌 재고 관리 시스템")
    
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

    # 경고 관리 섹션
    st.header(" 재고 경고 관리")
    
    # 필터링 시스템
    col1, col2 = st.columns([3,1])
    with col1:
        selected_factory = st.selectbox(
            "공장 선택",
            options=['전체'] + df['공장명'].unique().tolist()
        )
    
    with col2:
        selected_grade = st.multiselect(
            "경고 등급",
            options=df['경고등급'].unique(),
            default=['🚨 긴급', '⚠️ 주의']
        )

    # 데이터 필터링
    filtered_df = df[df['경고등급'].isin(selected_grade)]
    if selected_factory != '전체':
        filtered_df = filtered_df[filtered_df['공장명'] == selected_factory]

    # 경고 목록 표시
    if not filtered_df.empty:
        st.dataframe(
            filtered_df,
            column_config={
                "재고량": st.column_config.ProgressColumn(
                    "잔여량",
                    format="%d개",
                    min_value=0,
                    max_value=500
                ),
                "재고회전율": st.column_config.ProgressColumn(
                    "회전율",
                    format="%.2f",
                    min_value=0,
                    max_value=1.0
                )
            },
            height=400,
            use_container_width=True
        )
        
        # 슬랙 전송 기능
        selected_models = st.multiselect(
            "슬랙 전송할 모델 선택",
            filtered_df['모델명'].unique()
        )
        models_to_send = filtered_df[filtered_df['모델명'].isin(selected_models)]

        if st.button("📤 선택 모델 슬랙 전송", type="primary"):
            if not models_to_send.empty:
                send_slack_alert(models_to_send)
                st.toast("IGIS 시스템 알림 전송 완료", icon="✅")
            else:
                st.warning("전송할 모델을 선택해주세요.")
    else:
        st.success("✅ 모든 재고가 안전 수준입니다", icon="🛡️")