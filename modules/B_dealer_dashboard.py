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

    col1, col2, col3 = st.columns([1.1, 0.2, 1.5])

    with col1:
        st.warning("##### * 로그인 시 해당 매니저에 대한 데이터만 가져오도록 해야 합니다.")

        # 세션 초기화
        if "events" not in st.session_state or not isinstance(st.session_state.events, list):
            st.session_state.events = []

        if "edit_index" not in st.session_state:
            st.session_state.edit_index = None 

        if "confirm_delete_index" not in st.session_state:
            st.session_state.confirm_delete_index = None

        # ID 및 done 필드 보장
        for e in st.session_state.events:
            if 'id' not in e:
                e['id'] = str(uuid.uuid4())
            if 'done' not in e:
                e['done'] = False

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
                            'done': e['done'],
                            'description': e.get('description', '')
                        } for e in st.session_state.events
                    ])},
                    eventContent: function(info) {{
                        const done = info.event.extendedProps.done;
                        const checkbox = `<input type='checkbox' data-id='${{info.event.id}}' ${{done ? "checked" : ""}} style='position:absolute; right:10px; top:50%; transform:translateY(-50%);'/>`;
                        const titleStyle = done ? "color:#888;text-decoration:line-through;font-weight:normal;" : "font-weight:bold;";
                        const title = `<span style='${{titleStyle}}'>${{info.event.title}}</span>`;
                        return {{ html: `<div style='position:relative;'>${{title}}${{checkbox}}</div>` }};
                    }},
                    eventDidMount: function(info) {{
                      const checkbox = info.el.querySelector('input[type="checkbox"]');
                      if (checkbox) {{
                        checkbox.checked = info.event.extendedProps.done;
                      }}
                    }}
                }});
                calendar.render();

                // ✅ 체크박스 이벤트 핸들러
                document.addEventListener('change', function(e) {{
                    if (e.target.tagName === 'INPUT' && e.target.type === 'checkbox') {{
                        const eventId = e.target.getAttribute('data-id');
                        const checked = e.target.checked;

                        // Update event extendedProps for immediate visual effect
                        const event = calendar.getEventById(eventId);
                        if (event) {{
                            event.setExtendedProp('done', checked);
                        }}

                        window.parent.postMessage({{ event_id: eventId, done: checked }}, '*');
                    }}
                }});
            }});
        </script>
        </body>
        </html>
        """

        components.html(calendar_html, height=600)

        # ✅ 체크박스 상태 수신 및 반영
        clicked = st_javascript("""
        await new Promise((resolve) => {
          window.addEventListener("message", (event) => {
            if (event.data && event.data.event_id) {
              resolve(event.data);
            }
          });
        });
        """)

        if isinstance(clicked, dict) and 'event_id' in clicked:
            for e in st.session_state.events:
                if e.get('id') == clicked['event_id']:
                    e['done'] = clicked.get('done', False)
            st.rerun()

    with col3:
        st.warning("##### * 추후 유저 페이지 구축되면 '상담 추가/수정' 삭제 예정, 딜러는 상담 신청 내역 받아와서 확인만 하면 됩니다.")
        # 일정 추가/수정 폼
        with st.expander("##### 📝 상담 일정 추가/수정", expanded=False):
            if st.session_state.edit_index is not None:
                edit_event = st.session_state.events[st.session_state.edit_index]
                default_title = edit_event['title']
                default_date = datetime.fromisoformat(edit_event['start']).date()
                default_time = datetime.fromisoformat(edit_event['start']).time()
                default_description = edit_event.get('description', '')
            else:
                default_title = ""
                default_date = datetime.now().date()
                default_time = datetime.now().time().replace(second=0, microsecond=0)
                default_description = ''

            with st.form("event_form"):
                title = st.text_input("일정 제목", value=default_title)
                date = st.date_input("일정 날짜", value=default_date)
                time = st.time_input("시작 시간", value=default_time)
                description = st.text_area("상담 내용", value=default_description, max_chars=200, height=100)
                submitted = st.form_submit_button("저장")

                if submitted:
                    dt_str = datetime.combine(date, time).strftime("%Y-%m-%dT%H:%M:%S")
                    new_event = {
                        'id': str(uuid.uuid4()),
                        'title': title,
                        'start': dt_str,
                        'done': False,
                        'description': description
                    }

                    if st.session_state.edit_index is not None:
                        st.session_state.events[st.session_state.edit_index] = new_event
                        st.success("✅ 일정이 수정되었습니다.")
                        st.session_state.edit_index = None
                    else:
                        st.session_state.events.append(new_event)
                        st.success("✅ 일정이 추가되었습니다.")

                    st.rerun()

        # 일정 목록
        st.warning("##### * 일정 시간 순 정렬, 각 일정별 우측 끝 버튼 클릭하면 해당 '상담 정보' 창으로 이동")
        st.markdown("#### 📋 등록된 일정 목록")
        if not st.session_state.events:
            st.info("현재 등록된 일정이 없습니다.")
        else:
            for i, event in enumerate(st.session_state.events):
                col1, col2, col3, col4 = st.columns([5, 3, 1, 1])
                with col1:
                    st.write(f"📌 {event['title']}")
                with col2:
                    st.write(event['start'].replace("T", " "))
                with col3:
                    if st.button("✏️ 수정", key=f"edit_{i}"):
                        st.session_state.edit_index = i
                        st.rerun()
                with col4:
                    if st.button("❌ 삭제", key=f"delete_{i}"):
                        st.session_state.confirm_delete_index = i
                        st.rerun()

        # 삭제 확인 다이얼로그
        if st.session_state.confirm_delete_index is not None:
            idx = st.session_state.confirm_delete_index
            target = st.session_state.events[idx]
            st.warning(f"⚠️ '{target['title']}' 일정을 정말 삭제하시겠습니까?")
            col_confirm1, col_confirm2 = st.columns(2)
            with col_confirm1:
                if st.button("✅ 예, 삭제합니다"):
                    del st.session_state.events[idx]
                    st.session_state.confirm_delete_index = None
                    st.success("🗑️ 삭제 완료")
                    st.rerun()
            with col_confirm2:
                if st.button("❌ 아니요, 유지합니다"):
                    st.session_state.confirm_delete_index = None
                    st.info("삭제가 취소되었습니다.")
                    st.rerun()

    col_left, col_mid, col_right = st.columns([1, 1, 1])
    with col_left:
        st.subheader("🎯 목표 달성률 (개인/기업)")
        st.warning("##### * 선택한 기간(월/연/주)에 대한 현재 판매 달성률을 보여줍니다. 기준은 딜러 개인이 될 수도, 기업 전체가 될 수도 있습니다.")

        view_option = st.selectbox("기간 선택", ["월간", "연간", "주간"])
        target_sales = {
            "월간": 100,
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