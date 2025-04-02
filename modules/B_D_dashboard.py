import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import json
from datetime import datetime
import uuid
from streamlit_javascript import st_javascript  # 👈 꼭 설치 필요!
import plotly.graph_objects as go


def dashboard_ui():
    # 상담자 및 사번 세션 상태 초기화
    if "직원이름" not in st.session_state:
        st.session_state["직원이름"] = ""
    if "사번" not in st.session_state:
        st.session_state["사번"] = ""

    # 상담 내역 데이터 로드
    df = pd.read_csv("data/consult_log.csv")
    new_df = df.loc[df["담당직원"] == st.session_state["직원이름"], :]

    st.session_state.events = []
    for _, row in new_df.iterrows():
        if row.get("완료여부", 0) != 0:
            continue
        try:
            full_datetime_str = f"{row.get('상담날짜')} {row.get('상담시간')}"
            start_time = pd.to_datetime(full_datetime_str).isoformat()
        except Exception:
            start_time = datetime.now().isoformat()

        st.session_state.events.append({
            'id': str(uuid.uuid4()),
            'title': f"{row.get('이름', '이름 없음')} 고객님",
            'start': start_time,
            'description': row.get("상담내용", ""),
            '완료여부': row.get("완료여부", 0)
        })

    if st.session_state["직원이름"] == "":
        st.warning("딜러 정보를 먼저 등록하세요.")
        return
    
    col1, col2, col3 = st.columns([1, 0.2, 1.5])

    with col1:
        # 세션 초기화
        if "events" not in st.session_state or not isinstance(st.session_state.events, list):
            st.session_state.events = []

        if "edit_index" not in st.session_state:
            st.session_state.edit_index = None

        if "confirm_delete_index" not in st.session_state:
            st.session_state.confirm_delete_index = None

        # ✅ FullCalendar with checkbox + style
        calendar_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8" />
        <link href="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.css" rel="stylesheet" />
        <script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.8/index.global.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
            }}
            #calendar {{
                max-width: 800px;
                margin: 40px auto;
            }}
        </style>
        </head>
        <body>
        <div id='calendar'></div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const calendarEl = document.getElementById('calendar');
                const calendar = new FullCalendar.Calendar(calendarEl, {{
                    initialView: 'listWeek',
                    locale: 'ko',
                    height: 500,
                    events: {json.dumps([
                        {
                            'id': e['id'],
                            'title': f"<b>{e['title']}</b><br><span style='font-size: 12px; color: #666;'>{e.get('description', '')}</span>",
                            'start': e['start'],
                            'description': e.get('description', '')
                        } for e in st.session_state.events
                    ])},
                    eventContent: function(arg) {{
                        return {{ html: arg.event.title }};
                    }},
                }});
                calendar.render();
            }});
        </script>
        </body>
        </html>
        """

        components.html(calendar_html, height=600)

    with col3:
        # 일정 목록
        st.markdown("######")
        st.markdown("### 📋 예정된 상담 목록")
        
        upcoming_events = sorted(
            [e for e in st.session_state.events if pd.to_datetime(e["start"]) >= datetime.now() and e.get("완료여부", 0) == 0],
            key=lambda x: pd.to_datetime(x["start"])
        )[:3]

        if not upcoming_events:
            st.info("앞으로 예정된 상담이 없습니다.")
        else:
            if "confirm_finish_index" not in st.session_state:
                st.session_state.confirm_finish_index = None

            for i, event in enumerate(upcoming_events):
                st.markdown(f"""
                <div style="background-color: #f9f9f9; border: 1px solid #ccc; border-radius: 10px; padding: 15px; margin-bottom: 10px;">
                    <div style="font-size: 18px; font-weight: bold; color: #333;">📌 {event['title']}</div>
                    <div style="font-size: 14px; color: #555; margin: 5px 0 10px 0;">📝 {event.get('description', '상담내용 없음')}</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 13px; color: #777;">{event['start'].replace("T", " ")[:16]}</span>
                """, unsafe_allow_html=True)

                if st.button("완료", key=f"complete_{i}"):
                    # Find the matching event in the original df
                    match_condition = (
                        (df["이름"] == event['title'].replace(" 고객님", "")) &
                        (df["상담날짜"] + " " + df["상담시간"] == pd.to_datetime(event["start"]).strftime("%Y-%m-%d %H:%M"))
                    )
                    df.loc[match_condition, "완료여부"] = 1
                    df.to_csv("data/consult_log.csv", index=False)
                    st.success("상담 완료 처리되었습니다.")
                    st.rerun()

                st.markdown(f"""
                    </div>
                </div>
                """, unsafe_allow_html=True)

    col_left, col_midleft, col_mid, col_midright, col_right = st.columns([1, 0.1, 1, 0.1, 1])
    with col_left:
        st.subheader("🎯 목표 달성률 (개인/기업)")

        view_option = st.selectbox("기간 선택", ["주간", "월간", "연간"])
        target_sales = {
            "주간": 25,
            "월간": 150,
            "연간": 1000
        }
        current_sales = {
            "주간": 18,
            "월간": 69,
            "연간": 840
        }
        selected = view_option
        rate = current_sales[selected] / target_sales[selected] * 100

        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin-bottom: 10px; font-size: 16px;">
            <b>🎯 목표량:</b> {target_sales[selected]}건 &nbsp;&nbsp;&nbsp;
            <b>📊 실제 판매량:</b> {current_sales[selected]}건
        </div>
        """, unsafe_allow_html=True)

        # 동적 색상 설정
        if rate < 50:
            bar_color = "#FF6B6B"  # 빨강
            step_colors = ["#FFE8E8", "#FFC9C9", "#FFAAAA"]
        elif rate < 75:
            bar_color = "#FFD93D"  # 주황
            step_colors = ["#FFF3CD", "#FFE69C", "#FFD96B"]
        else:
            bar_color = "#6BCB77"  # 초록
            step_colors = ["#E8F5E9", "#C8E6C9", "#A5D6A7"]

        # 게이지 차트 생성
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=rate,
            title={'text': f"{selected} 목표 달성률 (%)"},
            delta={'reference': 100},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': bar_color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 33], 'color': step_colors[0]},
                    {'range': [33, 66], 'color': step_colors[1]},
                    {'range': [66, 100], 'color': step_colors[2]}
                ],
                'threshold': {
                    'line': {'color': "darkred", 'width': 4},
                    'thickness': 0.75,
                    'value': rate
                }
            }
        ))

        fig_gauge.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor="white",
            font=dict(color="darkblue", size=16)
        )

        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_mid:
        st.subheader("📢 회사 공지사항")

        st.write("")
    
        notices = [
            {
                "title": "🛠️ 4월 5일 서버 점검 예정입니다.",
                "details": [
                    "서버 점검 시간은 오전 2시부터 4시까지입니다.",
                    "해당 시간 동안 일부 서비스 이용이 제한됩니다.",
                    "점검 후 시스템 안정화 확인 예정입니다."
                ]
            },
            {
                "title": "✅ 1분기 판매 보고서 제출 마감: 4월 7일",
                "details": [
                    "보고서 제출 마감일은 4월 7일(일)입니다.",
                    "지연 제출 시 불이익이 있을 수 있습니다.",
                    "보고서는 지정 양식을 사용할 것."
                ]
            },
            {
                "title": "📈 이번 주 최우수 딜러는 홍길동 딜러입니다!",
                "details": [
                    "3월 마지막 주 기준 판매 1위 달성.",
                    "우수 고객 응대 평가도 최상위권입니다.",
                    "전사 포상 예정."
                ]
            },
            {
                "title": "📌 4월 목표는 총 150건 달성입니다. 함께 힘냅시다!",
                "details": [
                    "1분기 실적 기준 달성률은 85%입니다.",
                    "팀 단위 목표 공유 및 독려 부탁드립니다.",
                    "상세 현황은 인트라넷 참고."
                ]
            }
        ]

        for notice in notices:
            with st.expander(notice["title"]):
                for line in notice["details"]:
                    st.markdown(f"""
                    <div style="margin-bottom: 6px;">
                        <span style="font-size: 15px; font-weight: 500; color: #333;">• {line}</span>
                    </div>
                    """, unsafe_allow_html=True)

    with col_right:
        st.subheader("추가 기능 박스")
        st.warning("##### * 이 부분에 어떤 내용 들어갈지 아직은 미정")