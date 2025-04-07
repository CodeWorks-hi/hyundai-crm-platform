
    # 글로벌 재고 최적화, 공급망 관리
        # 재고 회전율 경고 시스템
            # 재고 회전율이 임계값 이하인 경우 슬랙으로 경고 메시지 전송

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests

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
def preprocess_data(df_inv):
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

    df_inv[['위도', '경도']] = pd.DataFrame(
        df_inv['공장명'].map(plant_location).tolist(),
        index=df_inv.index
    )

    np.random.seed(23)
    df_inv["월평균입고"] = np.random.randint(50, 500, size=len(df_inv))
    df_inv["월평균출고"] = np.random.randint(30, 400, size=len(df_inv))
    df_inv["재고회전율"] = (df_inv["월평균출고"] / df_inv["재고량"]).replace([np.inf, -np.inf], 0).fillna(0).round(2)

    df_inv['경고등급'] = np.select(
        [
            df_inv['재고회전율'] <= 0.15,
            df_inv['재고회전율'] <= 0.3,
            df_inv['재고회전율'] > 0.3
        ],
        ['🚨 긴급', '⚠️ 주의', '✅ 정상'],
        default='✅ 정상'
    ).astype(str)

    drop_cols = [
        '전장', '전폭', '전고', '배기량',
        '공차중량', 'CO2배출량', '연비', '기본가격'
    ]
    existing_columns = [col for col in drop_cols if col in df_inv.columns]
    df_inv = df_inv.drop(columns=existing_columns)

    return df_inv

# 슬랙 알림 함수 정의
def send_slack_alert(model_name, turnover_rate, plant=None, status=None, link=None):
    SLACK_WEBHOOK_URL = st.secrets["SLACK_WEBHOOK_URL"]
    emoji = "⚠️" if turnover_rate < 0.2 else "🔔"
    text = (
        f"{emoji} *재고 회전율 경고 발생!*\n"
        f"• 모델명: *{model_name}*\n"
        f"• 회전율: *{turnover_rate:.2f}*\n"
    )
    if plant:
        text += f"• 공장: `{plant}`\n"
    if status:
        text += f"• 생산상태: `{status}`\n"


    response = requests.post(SLACK_WEBHOOK_URL, json={"text": text, "link_names": 1})
    if response.status_code != 200:
        st.error(f"슬랙 전송 실패: {response.status_code} - {response.text}")

# 메인 UI 함수
def warning_ui():
    df_inv, df_list = load_data()
    df_inv = preprocess_data(df_inv.copy())

    with st.container(border=True):
        cols = st.columns([2, 1, 1, 2])
        cols[0].markdown("##### 🏭 통합 재고 관리 플랫폼 v2.1")

    threshold = st.select_slider(
        "⚠️ 경고 임계값 선택 (재고 회전율)",
        options=np.round(np.arange(0.1, 1.05, 0.05), 2),
        value=0.3
    )
    status_filter = st.radio(" 경고 대상 생산상태 선택", ["전체", "생산 중", "생산 종료"], horizontal=True)

    df_inv["경고"] = np.where(df_inv["재고회전율"] <= threshold, "⚠️ 경고", "정상")

    with st.expander(" 실시간 공장 위치 모니터링", expanded=True):
        fig = px.scatter_mapbox(
            df_inv,
            lat='위도',
            lon='경도',
            color='경고등급',
            size='재고량',
            hover_name='부품명',
            hover_data={'재고량': True, '재고회전율': ':.2f'},
            color_discrete_map={
                '🚨 긴급': '#FF4B4B',
                '⚠️ 주의': '#FFA500',
                '✅ 정상': '#00C853'
            },
            zoom=3,
            height=600
        )
        fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":40,"l":0,"b":0}, legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader(" 공장별 부품 재고 현황", divider="blue")
    fig = px.bar(
        df_inv.groupby(['공장명', '부품명'])['재고량'].sum().reset_index(),
        x='공장명',
        y='재고량',
        color='부품명',
        barmode='group',
        height=400,
        text_auto=True,
        labels={'재고량': '총 재고량'}
    )
    fig.update_layout(xaxis_title=None, yaxis_title="재고량(개)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader(" 위험 부품 상세 분석", divider="red")
    danger_df = df_inv[df_inv['재고량'] < 100]

    if not danger_df.empty:
        col1, col2 = st.columns(2)

        with col2:
            pie_df = danger_df.groupby('부품명')['재고량'].sum().reset_index()
            total_danger = pie_df['재고량'].sum()
            fig = px.pie(
                pie_df, names='부품명', values='재고량', hole=0.6,
                color='부품명', color_discrete_sequence=px.colors.sequential.Reds_r,
                title=f'<b>위험 부품 현황 (총 {total_danger}개)</b>'
            )
            fig.update_traces(textposition='inside', textinfo='percent+label', texttemplate='%{label}<br>%{percent} (%{value}개)', marker=dict(line=dict(color='white', width=2)), rotation=45)
            fig.update_layout(uniformtext_minsize=12, showlegend=False, margin=dict(t=50, b=20), title_x=0.5)
            st.plotly_chart(fig, use_container_width=True)

        with col1:
            trend_df = danger_df[['부품명', '월평균입고', '월평균출고']].copy()
            trend_df['입출고 차이'] = trend_df['월평균입고'] - trend_df['월평균출고']
            fig = px.bar(
                trend_df.sort_values('입출고 차이', ascending=False),
                x='부품명',
                y=['월평균입고', '월평균출고'],
                barmode='group', height=400,
                labels={'value': '월간 물동량(개)', 'variable': '구분'},
                color_discrete_map={'월평균입고': '#4B78DB', '월평균출고': '#F36E6E'},
                title='<b>월별 입출고 추이 비교</b>'
            )
            fig.update_layout(xaxis=dict(title=None, tickangle=-45, type='category'), yaxis=dict(gridcolor='#F0F2F6'), legend=dict(title='물동량 구분', orientation="h", yanchor="bottom", y=1.02), plot_bgcolor='white')
            fig.update_traces(texttemplate='%{y}개', textposition='outside', textfont_size=10)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ 모든 부품 재고가 안전 수준입니다.")

    st.subheader("🚨 실시간 경고 관리 시스템", divider="orange")
    col1, col2 = st.columns([1, 1])
    with col1:
        selected_factory = st.selectbox("공장 선택", ['전체'] + df_inv['공장명'].unique().tolist())
    with col2:
        grade_list = df_inv['경고등급'].astype(str).unique().tolist()
        valid_defaults = [g for g in ['🚨 긴급', '⚠️ 주의'] if g in grade_list]
        selected_grade = st.multiselect("경고 등급", options=grade_list, default=valid_defaults if valid_defaults else [])

    filtered_df = df_inv[df_inv['경고등급'].isin(selected_grade)]
    if selected_factory != '전체':
        filtered_df = filtered_df[filtered_df['공장명'] == selected_factory]

    if not filtered_df.empty:
        fig = px.treemap(
            filtered_df,
            path=['공장명', '모델명', '부품명'],
            values='재고량',
            color='재고회전율',
            color_continuous_scale='RdYlGn_r',
            height=800,
            title="<b>재고 위험 항목 계층 분석</b>"
        )
        st.plotly_chart(fig, use_container_width=True)

    warning_df = filtered_df[filtered_df["재고회전율"] <= threshold]
    with st.expander("📤 슬랙 경고 전송"):
        selected_models = st.multiselect("📌 슬랙으로 전송할 모델 선택", warning_df["모델명"].unique())
        slack_df = warning_df[warning_df["모델명"].isin(selected_models)]

        if st.button("🚨 슬랙 전송"):
            for _, row in slack_df.iterrows():
                send_slack_alert(
                    model_name=row["모델명"],
                    turnover_rate=row["재고회전율"],
                    plant=row.get("공장명", ""),
                    status=row.get("생산상태", ""),
                    link=f"https://example.com/cars/{row['모델명']}"
                )
            st.success("✅ 선택된 모델이 슬랙으로 전송되었습니다.")
