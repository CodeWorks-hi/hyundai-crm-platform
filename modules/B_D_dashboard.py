import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import json
from datetime import datetime
import uuid
from streamlit_javascript import st_javascript  # 👈 꼭 설치 필요!
import plotly.graph_objects as go

def dashboard_ui():
    # 상담 내역 데이터 로드
    df = pd.read_csv("data/consult_log.csv")
    new_df = df.loc[df["담당직원"] == "홍길동", :]

    col1, col2, col3 = st.columns([1, 0.2, 1.5])

    with col1:
        st.warning("##### * 로그인 시 해당 매니저에 대한 데이터만 가져오도록 해야 합니다.")

        # 세션 초기화
        if "events" not in st.session_state or not isinstance(st.session_state.events, list):
            st.session_state.events = []

        if "edit_index" not in st.session_state:
            st.session_state.edit_index = None

        if "confirm_delete_index" not in st.session_state:
            st.session_state.confirm_delete_index = None

        # CSV 기반 일정 항상 갱신
        st.session_state.events.clear()
        for _, row in new_df.iterrows():
            status = row.get('완료여부', '미정')
            try:
                start_time = pd.to_datetime(row.get("상담시간", datetime.now())).isoformat()
            except Exception:
                start_time = datetime.now().isoformat()

            st.session_state.events.append({
                'id': str(uuid.uuid4()),
                'title': f"{row.get('이름', '이름 없음')} 고객님",
                'start': start_time,
                'description': row.get("상담내용", "")
            })

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
                            'title': e['title'],
                            'start': e['start'],
                            'description': e.get('description', '')
                        } for e in st.session_state.events
                    ])}
                }});
                calendar.render();
            }});
        </script>
        </body>
        </html>
        """

        components.html(calendar_html, height=600)

        # ✅ 체크박스 상태 수신 및 반영
        # Removed checkbox event listener block

    with col3:
        st.warning("##### * 추후 유저 페이지 구축되면 '상담 추가/수정' 삭제 예정, 딜러는 상담 신청 내역 받아와서 확인만 하면 됩니다.")
        # 일정 목록
        st.warning("##### * 일정 시간 순 정렬, 각 일정별 우측 끝 버튼 클릭하면 해당 '상담 정보' 창으로 이동")
        st.markdown("#### 📋 등록된 일정 목록")
        if not st.session_state.events:
            st.info("현재 등록된 일정이 없습니다.")
        else:
            for i, event in enumerate(st.session_state.events):
                col1, col2, col3, col4 = st.columns([1.7, 4, 1.5, 1])
                with col1:
                    st.write(f"📌 {event['title']}")
                with col2:
                    st.text(f"📝 {event.get('description', '상담내용 없음')}")
                with col3:
                    st.write(event['start'].replace("T", " ")[:16])
                with col4:
                    if st.button("완료", key=f"complete_{i}"):
                        st.session_state.confirm_finish_index = i
                        st.rerun()
            if "confirm_finish_index" in st.session_state:
                idx = st.session_state.confirm_finish_index
                target = st.session_state.events[idx]
                st.warning(f"⚠️ '{target['title']}' 일정을 완료 처리하시겠습니까?")
                col_ok, col_cancel = st.columns(2)
                with col_ok:
                    if st.button("✅ 예, 완료합니다"):
                        for j, row in df.iterrows():
                            name_match = row.get("이름", "") in target["title"]
                            time_match = pd.to_datetime(row.get("상담시간", "")).strftime("%H:%M") in target["start"]
                            if name_match and time_match:
                                df.at[j, "완료여부"] = 1
                                break
                        df.to_csv("data/consult_log.csv", index=False)
                        del st.session_state.confirm_finish_index
                        st.success("✅ 완료 처리되었습니다.")
                        st.rerun()
                with col_cancel:
                    if st.button("❌ 아니요, 유지합니다"):
                        del st.session_state.confirm_finish_index
                        st.info("처리가 취소되었습니다.")
                        st.rerun()

    

    col_left, col_mid, col_right = st.columns([1, 1, 1])
    with col_left:
        st.subheader("🎯 목표 달성률 (개인/기업)")
        st.warning("##### * 선택한 기간(월/연/주)에 대한 현재 판매 달성률을 보여줍니다. 기준은 딜러 개인이 될 수도, 기업 전체가 될 수도 있습니다.")

        view_option = st.selectbox("기간 선택", ["월간", "연간", "주간"])
        target_sales = {
            "월간": 150,
            "연간": 1000,
            "주간": 25
        }
        current_sales = {
            "월간": 69,
            "연간": 840,
            "주간": 21
        }
        selected = view_option
        rate = current_sales[selected] / target_sales[selected] * 100

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
            title={'text': f"{selected} 목표 달성률"},
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
        st.warning("##### * 실시간으로 갱신되는 공지사항을 카드 형식으로 제공합니다. 회사의 지침 및 공지사항을 실시간으로 받아올 수 있는 코드 구현이 필요합니다.")
        notices = [
            "🛠️ 4월 5일 서버 점검 예정입니다.",
            "✅ 1분기 판매 보고서 제출 마감: 4월 7일",
            "📈 이번 주 최우수 딜러는 홍길동 딜러입니다!",
            "📌 4월 목표는 총 150건 달성입니다. 함께 힘냅시다!"
        ]
        for notice in notices:
            st.info(notice)

    with col_right:
        st.subheader("추가 기능 박스")
        st.warning("##### * 이 부분에 어떤 내용 들어갈지 아직은 미정")