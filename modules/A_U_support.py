# -*- coding: utf-8 -*-
import streamlit as st
import re
import os
from huggingface_hub import InferenceClient
from streamlit.components.v1 import html
from modules.A_U_kakao_channel import render_kakao_channel_add_button



# Hugging Face 모델 설정
TEXT_MODEL_ID = "mistralai/Mistral-Small-24B-Instruct-2501"
API_TOKEN = st.secrets.get("gemma_token")

if not API_TOKEN:
    st.error("❌ Hugging Face API 토큰이 설정되지 않았습니다.")


# FAQ 데이터셋 (검색 결과 [3] 구조 반영)
FAQS = [
            {
                "q": "🏠 대리점 방문 및 방문 상담 절차가 궁금해요?",
                "a": """**대리점 방문 가이드**
                - 지점 검색: '지점 찾기' 메뉴 > 지역/지점명 검색
                - 정보 확인: 지도 위치, 연락처, 운영시간 제공
                - 방문 예약: 온라인 예약 시스템 (날짜/시간 선택)
                """
            },
            {
                "q": "⚡ 전기차 구매 시 고려할 점은 무엇인가요?",
                "a": """**전기차 선택 가이드**  
        - 충전 인프라: 거주지역 충전소 밀집도 확인  
        - 주행 거리: 제조사 공인 주행거리 vs 실제 주행 조건 비교  
        - 보조금: 정부/지자체별 보조금 차이 (최대 1,200만원)  
        - 배터리 보증: 8년/16만km 기준 충전 용량 70% 이상 보장  
        - 충전 시간: 급속충전 30분(80%) vs 완속충전 6시간(100%)
        - 친환경 보조금 > 충전소 선택 > 충전소 현황 확인 가능 """
            },
            {
                "q": "🌍 차량의 환경 영향은 어떻게 되나요?",
                "a": """**탄소 배출량 분석**  
        - 가솔린 차량: 연간 평균 2.4톤 CO₂ 배출  
        - 전기차: 발전 방식에 따라 0.8~1.2톤 (한국 기준)  
        - 우리의 노력:  
        ▷ 2025년까지 공장 내 재생에너지 사용률 40% 목표  
        ▷ 배터리 재활용 프로그램 운영 (수명 종료 배터리 90% 재활용)"""
            },
            {
                "q": "🔧 정기 정비 일정은 어떻게 확인하나요?",
                "a": """**스마트 관리 시스템**  
        1. 대리점 검색> '정비소 찾기' 메뉴 접속  
        2. 서비스 센터 전화번호 확인 가능
        3. 주행거리 기반 맞춤 점검 항목 제공  
        4. 주요 관리 주기:  
        - 엔진오일: 15,000km/1년  
        - 타이어 로테이션: 10,000km  
        - 배터리 점검: 30,000km  
        5. 푸시 알림 서비스 신청 가능"""
            },
            {
                "q": "🛡️ 제조사 보증은 무엇을 포함하나요?",
                "a": """**종합 보증 패키지**  
        - 기본 보증: 3년/6만km (차체 부식 7년)  
        - 파워트레인: 5년/10만km  
        - 고전압 배터리: 8년/16만km  
        - 제외 항목:  
        ▷ 소모품 부품 (와이퍼, 브레이크 패드 등)  
        ▷ 사고 수리 이력이 있는 경우  
        ▷ 권장 정비 미이행 시"""
            },
            {
                "q": "🚗 중고차 구매 시 주의사항은 무엇인가요?",
                "a": """**중고차 체크리스트**  
        - 반드시 확인:  
        ① 차대번호 조회 (사고 이력 확인)  
        ② 엔진 오일 상태 점검  
        3. 주요 계기판 경고등 점검  
        - 권장 서비스:  
        ▷ 공인 인증 중고차 프로그램 활용  
        ▷ 전문 검사관 동반 검차  
        ▷ 차량 구매 계약서 반드시 서면 작성"""
            },
            {
                "q": "🏠 서비스 센터 방문 없이 정비가 가능한가요?",
                "a": """**모바일 서비스 프로그램**  
        - 가능 서비스:  
        ▷ 소프트웨어 업데이트  
        ▷ 배터리 점검  
        ▷ 타이어 공기압 보충  
        - 이용 방법:  
        ① 포털에서 서비스 신청  
        ② 기술자가 지정 장소 방문  
        ③ 실시간 작업 영상 제공  
        - 비용: 기본 출동비 3만원 (보증료 무료)"""
            },
            {
                "q": "📊 예상 유지비를 어떻게 계산할 수 있나요?",
                "a": """**종합 유지비 계산기**  
        - 고려 요소:  
        ▷ 연간 주행거리  
        ▷ 유류비/전기요금  
        ▷ 보험료 등급  
        ▷ 주차장/톨게이트 비용  
        - 제공 기능:  
        ▶ 지역별 평균 유지비 비교  
        ▶ 친환경차 vs 내연기관차 경제성 비교  
        ▶ 5년 총 소유 비용(TCO) 시뮬레이션"""
            },
            {
                "q": "🔌 전기차 충전 인프라는 어떻게 되나요?",
                "a": """**충전 네트워크 현황**  
        - 전국 2,300개 충전소 운영 
        - 친환경 보조금 >  충전소 선택 > 충전소 현황 확인 가능 
        - 주요 제휴처:  
        ▷ 고속도로 휴게소 100% 설치  
        ▷ 대형 마트/영화관 주차장  
        ▷ 주요 도시 공용 주차장  
        - 홈충전기 지원:  
        ▶ 설치비 50% 지원 (최대 70만원)  
        ▶ 야간 할인 요금제 연계"""
            },
            {
                "q": "🆘 긴급 출동 서비스는 제공되나요?",
                "a": """**24시간 긴급 지원 시스템**  
        - 지원 항목:  
        ▷ 배터리 점프 스타트  
        ▷ 타이어 펑크 수리  
        ▷ 긴급 견인 서비스  
        - 이용 방법:  
        ① 전용 앱 'SOS' 버튼 클릭  
        ② 위치 정보 자동 전송 료
        ③ 평균 출동 시간 35분 이내  
        - 비용: 기본 보증료 무료"""
            },
            {
                "q": "🎨 차량 커스터마이징 옵션은 무엇이 있나요?",
                "a": """**맞춤 제작 프로그램**  
        - 외장: 15가지 색상 + 5가지 특수 도장  
        - 내장:  
        ▷ 시트 소재 (나파 가죽/친환경 소재)  
        ▷ 계기판 스킨 변경  
        ▷ 앰블럼 커스텀 각인  
        - 성능:  
        ▶ ECU 튜닝 (마력 10% 향상)  
        ▶ 배기 음향 조절 시스템  
        - 납기: 6-8주 소요"""
            }
        ]

# 시스템 프롬프트 생성
def build_system_prompt():
    """검색 결과 [2][4] 반영한 프롬프트 생성"""
    newline = '\n'  # 개행 문자 변수화
    faq_items = []
    
    try:
        for idx, faq in enumerate(FAQS, 1):
            formatted_answer = faq['a'].replace(newline, f'{newline}   - ')
            faq_items.append(
                f"{idx}. [{faq['q']}]{newline}"
                f"   - {formatted_answer}"
            )
    except KeyError as e:
        st.error(f"FAQ 데이터 구조 오류: {str(e)}")
        return ""

    return f"""
            [시스템 역할]
            현대자동차 고객센터 AI 어시스턴트입니다.
            아래 FAQ 데이터를 기반으로 전문적이고 정확한 답변을 제공해주세요.
  

            [FAQ 데이터]
            {newline.join(faq_items)}

			[응답 규칙]
			1. FAQ 내용 100% 준수하여 답변 (지식 범위 외 질문 시 전화번호 안내)
			2. 숫자/금액 → 한글 표기 (예: 50 → 오십, 1,200만원 → 천이백만 원)
			3. 전문 용어 최소화 → 초보자 이해 가능한 설명
			4. 마크다운 사용 금지 → 평문으로 간결하게 표현
			5. 차량 모델명은 [브랜드-모델-트림] 형식 표기 (예: 현대-아이오닉6-스탠다드)
			6. 브랜드 이미지에 맞는 존댓말 사용 (예: ~합니다, ~입니다)
			7. 모르는 질문 처리: "해당 정보는 준비 중입니다. 고객센터(02-1234-5678)로 문의주세요"
			8. 질문에 대한 답변만 작성 (예: "네, 맞습니다" → "맞습니다")
			9. 질문에 대한 답변만 작성 (예: "아니요, 아닙니다" → "아닙니다")
            10. 아래의 FAQ 형식으로 답변 작성
            "q": " 서비스 센터 방문 없이 정비가 가능한가요?",
            "a": 안녕하세요! 고객님의 편의를 위해 방문 정비 서비스를 제공하고 있습니다. 

                    **방문 가능 서비스**  
                    ✔ 소프트웨어 최신 버전 업데이트  
                    ✔ 고전압 배터리 성능 점검  
                    ✔ 타이어 공기압 무료 보충  

                     **이용 방법**  
                    1. 포털에서 [모바일 서비스 신청] 메뉴 접속  
                    2. 원하는 날짜/시간 선택 후 신청 완료  
                    3. 전문 기술자가 지정 장소로 방문  
                    4. 실시간 영상으로 작업 과정 확인  

                    **비용 안내**  
                    - 기본 출동비: 3만원 (보증 기간 내 무료)  
                    - 부품 교체 시 별도 비용 발생  

                    언제든지 홈페이지 또는 고객센터(1544-1234)로 문의주세요!  
                    고객님의 소중한 시간을 아껴드리기 위해 최선을 다하겠습니다.

                        """

def generate_gemma_response(user_input: str) -> str:
    if not API_TOKEN:
        return "❌ 시스템 오류: 관리자에게 문의해주세요"
    try:
        client = InferenceClient(provider="auto", api_key=API_TOKEN)
        completion = client.chat.completions.create(
            model="mistralai/Mistral-Small-3.1-24B-Instruct-2503",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{build_system_prompt()}\n\n[질문]\n{user_input}\n[답변]"
                        }
                    ]
                }
            ],
        )
        return completion.choices[0].message["content"].strip()
    except Exception as e:
        if "401" in str(e):
            return "⚠️ 인증 오류: API 토큰을 재발급해주세요"
        return f"⚠️ 시스템 오류: {str(e)}"

def clean_response(text: str) -> str:
    """검색 결과 [1] 데이터 클렌징 규칙 적용"""
    text = re.sub(r'\*\*|```', '', text)
    text = re.sub(r'(\d+)만원', lambda x: f"{x.group(1)}만 원", text)  # 금액 포맷팅
    return text[:1500].strip()

def support_ui():
    """IGIS 통합 UI (검색 결과 반영)"""
    # 헤더 섹션 
    col1, col2 = st.columns([8, 1])  # columns 인수 추가
    
    with col2:
        render_kakao_channel_add_button()
        
    with col1:
        st.markdown("## 고객 지원 센터")

    # FAQ 섹션
    st.markdown("### ❓ 자주 묻는 질문")
    for faq in FAQS:
        with st.expander(faq["q"], expanded=False):
            st.markdown(faq["a"].replace('\n', '  \n'))  # 마크다운 개행 처리
        
    st.markdown("---")    

    # AI 채팅 인터페이스
    st.markdown("### 실시간 AI 상담")

    # 사용자 질문 입력
    st.markdown("""
                <style>
                    .faq-guide { 
                        background-color: #f0f2f6;
                        padding: 15px;
                        border-radius: 10px;
                        border-left: 4px solid #2A7FFF;
                        margin: 20px 0;
                    }
                </style>
                <div class="faq-guide">
                    <div style="color:#2A7FFF; font-size:18px; margin-bottom:8px;"> 질문 전 확인해주세요!</div>
                    <div style="color:#333;">
                        <b>아래 FAQ에서 원하는 답변을 먼저 찾아보세요</b><br>
                        • 자주 묻는 질문을 모아둔 <span style="color:#2A7FFF;">'❓ 자주 묻는 질문'</span> 섹션 확인부탁드립니다.<br>
                        • 이미 작성된 답변을 바탕으로 빠르게 문제 해결 가능 합니다.
                    </div>
                    <div style="margin-top:10px; font-size:14px; color:#666;">
                        ※ FAQ의 질문 내용은 바탕으로 하단 입력창을 이용해 질문해주세요😍
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    user_input = st.text_area("질문을 입력해 주세요 ", placeholder="예: 대리점 방문 및 방문 상담 절차가 궁금해요?", height=100)

    # 질문 결과 출력 (디자인 개선 및 q/a 제거 포함)
    if st.button("질문하기"):
        if user_input.strip():
            with st.spinner("AI 분석 중..."):
                response = generate_gemma_response(user_input)
            
            # 시각적으로 정리된 박스 형태로 출력
            st.markdown(f"""
            <div style='border:1px solid #ccc; padding:20px; border-radius:10px; background-color:#f9f9f9; margin-top:20px; line-height:1.6; font-size:15px;'>
                {response}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("질문을 입력해주세요.")

    # 부가 정보 섹션
    st.markdown("---")
    st.markdown("#####  📞 추가 상담 안내")
    info_cols = st.columns(3)  # 2개 컬럼 생성
    
    with info_cols[0]:  # 첫 번째 컬럼
        st.markdown("**전화**\n 1544-1234\n (평일 10:00~17:00)")
    
    with info_cols[1]:  # 두 번째 컬럼
        st.markdown("**AI 상담**\n 24시간 상담 가능\n (상담사 연결 시 대기시간 발생)")

    with info_cols[2]:  # 두 번째 컬럼
        st.markdown("**이메일**\n schoi1278@gmail.com\n")
        
