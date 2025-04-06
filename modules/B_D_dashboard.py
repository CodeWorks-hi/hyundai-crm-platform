import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import json
from datetime import datetime
import uuid
import plotly.graph_objects as go
import re
import requests
from huggingface_hub import InferenceClient
from bs4 import BeautifulSoup


TEXT_MODEL_ID = "google/gemma-2-9b-it"

def get_huggingface_token(model_type):
    tokens = {"gemma": st.secrets.get("HUGGINGFACE_API_TOKEN_GEMMA")}
    return 'hf_' + tokens.get(model_type)

def generate_answer(request: str, keywords: str, model_name: str = TEXT_MODEL_ID) -> str:
    token = get_huggingface_token("gemma")
    if not token:
        st.error("Hugging Face API 토큰이 없습니다.")
        return ""

    system_prompt = """
    [시스템 지시 사항]
    ### 1. 질문 분석
    - 사용자 질문의 핵심 키워드 추출
    - 키워드 기반으로 필요로 하는 정보 유형 파악
    - 답변에 필요한 키워드 유형 파악

    ### 2. 답변 키워드 분석
    - 응답자가 제공한 문구에서 핵심 키워드 추출
    - 1단계에서 파악한 필요 정보 유형과 비교하여 분석
    - 필요 정보와 일치하는 내용만 답변 생성에 활용
    
    ### 3. 최종 답변 생성
    - 응답자가 제공한 핵심 키워드 기반 답변 생성
    - 친절하고 전문적인 어조로 100자 이내로 작성
    - 고객의 요청에 매우 부합하는 정보만 제공
    - 답변이 어려운 경우 현장 상담 유도
    """

    full_prompt = f"{system_prompt}\n\n[사용자 질문]\n\n{request}\n\n[답변 키워드]\n\n{keywords}"
    
    try:
        client = InferenceClient(model=model_name, token=token)
        response = client.text_generation(
            prompt=f"""
            다음 사용자 질문에 대한 답변을 현대자동차 전문가 입장에서 100자 이내로 답변해줘.
            사용자의 질문은 순전히 필요 정보 파악하기 위한 참고용이야. 너무 얽매이지 마.
            매우 중요한 점. 줄 바꿈은 절대로 하지마. 한 줄로 이루어진 답변이어야 해.
            근거를 토대로 답변해야 해. 애매한 경우 현장 상담을 유도해.
            \n{full_prompt}""",
            max_new_tokens=1000,
            temperature=0.2
        )
        return response
    except Exception as e:
        st.error(f"텍스트 생성 오류: {e}")
        return ""


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
            'contact': row.get('전화번호', '전화번호 없음'),
            'description': row.get("요청사항", ""),
            '완료여부': row.get("완료여부", 0)
        })

    if st.session_state["직원이름"] == "":
        st.warning("딜러 정보를 먼저 등록하세요.")
        return
    
    col1, col2, col3 = st.columns([1.2, 0.1, 1.5])

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
                            'title': f"<b>{e['title']}</b><br><span style='font-size: 12px; color: #666;'>{e.get('description', '')}</span><br><span style='font-size: 11px; color: #999;'>{e.get('contact', '')}</span>",
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
        st.write("")

        upcoming_events = sorted(
            [e for e in st.session_state.events if pd.to_datetime(e["start"]) >= datetime.now() and e.get("완료여부", 0) == 0],
            key=lambda x: pd.to_datetime(x["start"])
        )[:4]

        if not upcoming_events:
            st.info("앞으로 예정된 상담이 없습니다.")
        else:
            if "confirm_finish_index" not in st.session_state:
                st.session_state.confirm_finish_index = None

            for i, event in enumerate(upcoming_events):
                col_event, col_button = st.columns([4, 1])
                with col_event:
                    st.markdown(f"""
                    <div style="background-color: #f9f9f9; border: 1px solid #ccc; border-radius: 8px; padding: 10px 12px; margin-bottom: 6px;">
                        <div style="font-size: 16px; font-weight: bold; color: #333; margin-bottom: 4px;">📌 {event['title']}</div>
                        <div style="font-size: 13.5px; color: #555; margin-bottom: 6px;">📝 {event.get('description', '상담내용 없음')}</div>
                        <div style="font-size: 13px; color: #777;">{event['start'].replace("T", " ")[:16]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_button:
                    st.write("")  # vertical spacing
                    st.write("")  # vertical spacing
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

    col_left, col_midleft, col_mid, col_midright, col_right = st.columns([0.9, 0.1, 0.8, 0.1, 0.7])
    with col_left:
        st.subheader("🎯 개인 목표 달성률")

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
        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin-bottom: 10px; font-size: 18px;">
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
            title={'text': f"{st.session_state['직원이름']} 매니저님의 {selected} 목표 달성률 (%)"},
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

        if rate < 50:
            st.info("🚀 아직 목표에 도달하려면 시간이 필요해요. 오늘 한 건 더 도전해보는 건 어떨까요?")
        elif rate < 75:
            st.success("💪 잘하고 있어요! 조금만 더 힘내면 목표 달성이 눈앞입니다.")
        else:
            st.success("🎉 훌륭합니다! 이미 목표치에 근접했어요. 멋진 마무리 기대할게요.")

    with col_mid:
        st.markdown("### 상담 요청 답변")

        colL, colR = st.columns(2)
        with colL:
            selected_name = st.text_input("고객 성명 입력", key="dash_name")
        with colR:
            selected_contact = st.text_input("고객 연락처 입력", key="dash_contact")  

        if selected_name and selected_contact:
            cr_df = pd.read_csv("data/consult_log.csv")
            mask = (cr_df['이름'] == selected_name) & (cr_df['전화번호'] == selected_contact) & (cr_df["목적"] == "문의") & (cr_df["완료여부"] == 0)
            matched_requests = cr_df.loc[mask, "요청사항"].tolist()
            
            if matched_requests:
                st.markdown("#### 🙋 고객 질문")
                st.markdown(f"""
                <div style="background-color:#f9f9f9;padding:12px 16px;border-left:5px solid #1e90ff;border-radius:6px;font-size:14.5px">
                {matched_requests[0]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("조건에 맞는 문의가 존재하지 않습니다.")
        
        memo = st.text_area("답변 내용을 입력하세요", height=68, label_visibility="collapsed")

        if st.button("✅ 저장", use_container_width=True):
            cr_df = pd.read_csv("data/consult_log.csv")
            mask = (cr_df['이름'] == selected_name) & (cr_df['전화번호'] == selected_contact) & (cr_df["목적"] == "문의")
 
            if not cr_df.loc[mask & (cr_df["완료여부"] == 0), :].empty:
                if mask.any():
                    result_txt = generate_answer(matched_requests[0], memo, model_name=TEXT_MODEL_ID) 
                    result_txt = result_txt.replace("[최종 답변]", "")
                    result_txt = result_txt.strip(" ").strip(",").strip(" ").replace("\n", "").replace("\r", "").replace("  ", " ")

                    cr_df.loc[mask & (cr_df["완료여부"] == 0), "답변내용"] = result_txt
                    cr_df.loc[mask & (cr_df["완료여부"] == 0), "완료여부"] = 1

                    # 원본 CSV 로드 및 해당 행만 수정
                    full_df = pd.read_csv("data/consult_log.csv")
                    full_df.update(cr_df[["이름", "전화번호", "목적", "답변내용", "완료여부"]])
                    full_df.to_csv("data/consult_log.csv", index=False)

                    st.success("✅ 답변 내용이 저장되었습니다.")
                else:
                    st.warning("해당 조건에 맞는 문의가 없습니다.")
            else:
                if not cr_df.loc[mask & (cr_df["완료여부"] == 1), :].empty:
                    st.warning("해당 조건에 맞는 문의에 대한 답변이 이미 완료되었습니다.")

        st.markdown("---")

        st.markdown("### ✅ 최근 완료 상담")
        st.write("")

        completed_df = df[(df["담당직원"] == st.session_state["직원이름"]) & (df["완료여부"] == 1)]
        recent_done = completed_df.sort_values(by=["상담날짜", "상담시간"], ascending=False).head(2)

        if recent_done.empty:
            st.info("아직 완료된 상담이 없습니다.")
        else:
            for _, row in recent_done.iterrows():
                st.markdown(f"""
                <div style="background-color: #f4f4f4; border: 1px solid #ddd; border-radius: 8px; padding: 10px 12px; margin-bottom: 8px;">
                    <div style="font-size: 15px; font-weight: 600; color: #333;">👤 {row['이름']} ({row['전화번호']})</div>
                    <div style="font-size: 13px; color: #555;">📅 {row['상담날짜']} {row['상담시간']}</div>
                    <div style="font-size: 13px; color: #777; margin-top: 4px;">📝 {row['상담내용']}</div>
                </div>
                """, unsafe_allow_html=True)
       

    with col_right:
        st.subheader("📢 회사 공지사항")
        st.write("")

        info_df = pd.read_csv("data/information.csv")
        info_df["게시일자"] = pd.to_datetime(info_df["게시일자"])
        info_df = info_df.sort_values(by="게시일자", ascending=False).head(7)

        for _, row in info_df.iterrows():
            with st.expander(row["제목"]):
                for col in ["내용1", "내용2", "내용3"]:
                    if pd.notna(row[col]):
                        st.markdown(f"""
                        <div style="margin-bottom: 6px;">
                            <span style="font-size: 15px; font-weight: 500; color: #333;">• {row[col]}</span>
                        </div>
                        """, unsafe_allow_html=True)