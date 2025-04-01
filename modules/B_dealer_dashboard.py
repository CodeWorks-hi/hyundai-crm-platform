import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import json
from datetime import datetime
import uuid
from streamlit_javascript import st_javascript  # 👈 꼭 설치 필요!
import sys
import streamlit as st


def dashboard_ui():
    st.write("현재 사용 중인 Python 버전:", sys.version)
    st.markdown("### 📅 일정 관리 캘린더")

    # 상담 내역 데이터 로드
    df = pd.read_csv("data/consult_log.csv")

    col1, col2, col3 = st.columns([1.1, 0.2, 1.5])

    with col1:
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
        st.warning("추후 유저 페이지 구축되면 삭제 예정, 딜러는 상담 신청 내역 받아와서 확인만 하면 됩니다.")
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