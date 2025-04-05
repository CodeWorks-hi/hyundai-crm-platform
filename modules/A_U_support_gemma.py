# +---------+
# | 고객 센터 - Google Gemma-2-9B-IT 모델 API 호출 |
# +---------+

import json
import re
import streamlit as st
from huggingface_hub import InferenceClient

# 모델 및 API 설정
TEXT_MODEL_ID = "google/gemma-2-9b-it"
API_TOKEN = st.secrets.get("HUGGINGFACE_API_TOKEN")

# Q&A 데이터셋 (검색 결과 기반)
FAQS = [
        {
            "q": "♻️ 중고차 보상 판매 프로그램이 있나요?",
            "a": """**중고차 보상 판매 제도 안내**  
    - 기존 차량을 판매하고 새 차로 교체 시 추가 혜택 제공  
    - 보상 금액은 차량 연식, 상태, 주행 거리 등 기준에 따라 산정  
    - 참여 방법:  
        ① 고객 포털에서 [보상 판매 신청서] 작성  
        ② 전문 감정 후 견적 안내  
        ③ 신규 차량 계약 시 보상 금액 차감  
    - 보상 판매 시 최대 50만원 추가 지원 이벤트 진행 중"""
        },
        {
            "q": "💸 차량 유지비는 얼마나 드나요?",
            "a": """**유지비 계산기 / 월 운영비 시뮬레이터**  
    ▶ [고객 포털 > 경제 인사이트] 메뉴에서 제공  

    - 예상 연 주행거리 입력 시 월 평균 유지비 자동 계산  
    - 포함 항목:  
        ▷ 연료비 / 전기차 충전비  
        ▷ 정기점검 및 정비 비용  
        ▷ 보험료 / 세금 / 주차비  

    - 예: 연 15,000km 기준  
        - 가솔린 차량: 월 약 35만원  
        - EV 차량: 월 약 22만원"""
        },
        {
            "q": "💬 상담사 연결 없이 채팅 상담 가능한가요?",
            "a": """**AI 챗봇 기반 고객지원 서비스**  
    - [고객 포털 > 1:1 채팅상담] 메뉴에서 사용 가능 예정  
    - 챗봇으로 가능한 상담 항목:  
        ▷ 차량 추천 / 구매 프로세스 안내  
        ▷ 정비 일정 조회 및 예약  
        ▷ 포인트 사용 / 잔액 조회  
        ▷ 경제 지표 기반 차량 가격 시뮬레이션  

    - 추후 OpenAI 기반 대화형 챗봇 연동 예정"""
        },
        {
            "q": "🔁 차량 재구매 시 어떤 혜택이 있나요?",
            "a": """**재구매 고객 우대 프로그램**  
    - 동일 브랜드 차량 2회 이상 구매 고객 대상  
    - 혜택 예시:  
        ✓ 보증 연장 + 프리미엄 정비 쿠폰  
        ✓ 전용 고객 등급 부여 (Platinum+)  
        ✓ 시승권/초청 행사 제공  
    - 최근 5년 이내 차량 구매 이력이 있는 고객은 자동 적용"""
        },
        {
            "q": "📍 여러 딜러 중 어디가 가장 유리한가요?",
            "a": """**딜러사 비교 팁**  
    - [매장 찾기] 메뉴에서 지역별 딜러 평가/리뷰 확인 가능  
    - 비교 항목:  
        ✓ 평균 출고 소요일  
        ✓ 시승 차량 보유 여부  
        ✓ 프로모션 진행 내역  
        ✓ 서비스 만족도 점수  
    - 딜러사 별 인센티브/사은품도 상이하니 꼼꼼히 확인하세요!"""
        }
    ]
]

# 입력/출력 처리 함수
def clean_input(text: str) -> str:
    return re.sub(r"\b(해줘|알려줘|설명해 줘)\b", "", text, flags=re.IGNORECASE).strip()

def format_response(text: str) -> str:
    cleaned = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\n{3,}', '\n\n', cleaned)

# AI 응답 생성 함수
def generate_gemma_response(user_input: str) -> str:
    if not API_TOKEN:
        return "❌ API 토큰이 설정되지 않았습니다. 관리자에게 문의해주세요."
    
    try:
        # FAQ 컨텍스트 생성
        context = "\n".join([f"Q: {item['q']}\nA: {item['a']}" for item in FAQS])
        
        client = InferenceClient(model=TEXT_MODEL_ID, token=API_TOKEN)
        response = client.text_generation(
            prompt=f"""**[현대자동차 고객지원 시스템]**
{context}

**사용자 질문:** {user_input}
**AI 어시스턴트:**""",
            max_new_tokens=1000,
            temperature=0.7,
            return_full_text=False
        )
        return format_response(response)
    except Exception as e:
        return f"⚠️ 오류 발생: {str(e)}"

# Streamlit UI 컴포넌트
def gemma_ui():
    st.markdown("#### 🤖 GEMMA AI 고객 지원")
    st.markdown("""
    차량 구매부터 유지관리까지 모든 질문에 답변드립니다.  
    아래 입력창에 궁금한 내용을 입력해주세요.
    """)
    
    # 사용자 입력
    user_input = st.text_input(
        "질문을 입력하세요 (예: 중고차 보상 판매 프로그램이 어떻게 되나요?)",
        key="gemma_input"
    )
    
    # 질문 처리
    if st.button("질문 제출", key="gemma_submit"):
        if not user_input.strip():
            st.warning("질문을 입력해주세요.")
            return
            
        with st.spinner("AI 분석 중..."):
            cleaned_input = clean_input(user_input)
            response = generate_gemma_response(cleaned_input)
            
            # 결과 표시
            with st.expander("💬 AI 답변 보기", expanded=True):
                st.markdown(response)
                
            # FAQ 매칭 시 추가 정보 표시
            if any(faq['q'] in user_input for faq in FAQS):
                st.image("https://example.com/faq_banner.jpg", width=300)
