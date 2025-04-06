"""
This script provides a Streamlit application that allows users to ask questions related to Hyundai vehicles. 
It utilizes the Hugging Face API to generate answers based on user input and logs the questions and answers to a CSV file.
"""

import streamlit as st
import pandas as pd
from huggingface_hub import InferenceClient
import os

TEXT_MODEL_ID = "google/gemma-2-9b-it"
LOG_PATH = "data/qna_log.csv"

# ==============================
# Token Handling
# ==============================

# Hugging Face API 토큰 불러오기
def get_huggingface_token(model_type):
    # 지정된 모델 유형에 대한 Hugging Face API 토큰을 검색합니다.
    tokens = {"gemma": st.secrets.get("HUGGINGFACE_API_TOKEN_GEMMA")}
    return 'hf_' + tokens.get(model_type)

# ==============================
# AI Inference
# ==============================

# 답변 생성 함수
def get_car_info_based_on_question(user_input: str, model_name: str = TEXT_MODEL_ID) -> str:
    # 사용자의 입력에 기반하여 지정된 모델을 사용하여 응답을 생성합니다.
    token = get_huggingface_token("gemma")
    if not token:
        return "❌ Hugging Face API 토큰이 설정되어 있지 않습니다."

    prompt = f"""
    [시스템 지시 사항]
    ### 상담 내용 분석
    - 입력된 글의 핵심 키워드 추출
    - 키워드 기반으로 태그 생성
    
    [입력 예시 및 태그 출력 예시]
    각 상담 내용에는 고객의 관심사/상황에 따라 다음과 같은 카테고리로 태그를 지정하세요:
    - 구매단계: 관심, 구매 가능성 있음, 구매 결정, 구매 미정
    - 방문여부: 첫방문, 재방문 예정, 재방문 완료
    - 관심사: 전기차 관심, SUV 관심, 혜택 관심, 시승 희망, 안전 우선, 연비 중시, 공간 우선
    - 기타: 1인용, 가족용, 부모님 동승, 예산 3000 이하, 상담 지속, 피드백 요청
    
    질문: {user_input.strip()}
    답변:
    """

    try:
        client = InferenceClient(model=model_name, token=token)  # 모델과 토큰으로 InferenceClient 초기화
        response = client.text_generation(
            prompt=prompt,
            max_new_tokens=512,  # 생성되는 새로운 토큰 수 제한
            temperature=0.5,     # 출력의 무작위성 조절
        )
        return response.strip()  # 생성된 응답 반환
    except Exception as e:
        return f"오류 발생: {e}"  # 추론 중 발생하는 예외 처리

# ==============================
# Tag Extraction
# ==============================

def extract_tags_from_answer(answer: str) -> str:
    # 생성된 답변에서 키워드를 추출하여 태그 형태로 반환합니다.
    tag_prompt = f"""
    다음 설명에서 핵심 키워드를 쉼표로 구분된 태그 형태로 뽑아주세요. 단어 수는 1~2단어로 간결하게 해주세요.
    
    설명: {answer.strip()}
    태그:
    """
    token = get_huggingface_token("gemma")
    try:
        client = InferenceClient(model=TEXT_MODEL_ID, token=token)  # 태그 추출을 위한 InferenceClient 초기화
        response = client.text_generation(
            prompt=tag_prompt,
            max_new_tokens=30,  # 태그 추출을 위한 새로운 토큰 수 제한
            temperature=0.3,    # 출력의 무작위성 조절
        )
        return response.strip()  # 추출된 태그 반환
    except Exception as e:
        return "일반"  # 오류 발생 시 기본 태그 반환

# ==============================
# Data Storage
# ==============================

# CSV 저장 함수
def save_to_csv(question: str, answer: str):
    # 질문, 답변 및 태그를 CSV 파일에 저장합니다.
    tag_str = extract_tags_from_answer(answer)  # 답변에서 태그 추출

    new_row = pd.DataFrame([{
        "질문": question,
        "답변": answer,
        "답변 태그": tag_str,
        "날짜": pd.Timestamp.now().strftime("%Y-%m-%d"),  # 현재 날짜 가져오기
        "시간": pd.Timestamp.now().strftime("%H:%M:%S")   # 현재 시간 가져오기
    }])

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)  # 로그 파일을 위한 디렉토리가 존재하지 않으면 생성

    if os.path.exists(LOG_PATH):
        df = pd.read_csv(LOG_PATH)  # 기존 로그 데이터 읽기
        df = pd.concat([df, new_row], ignore_index=True)  # 기존 데이터에 새 행 추가
    else:
        df = new_row  # 로그 파일이 없으면 새로운 DataFrame 생성

    df.to_csv(LOG_PATH, index=False)  # DataFrame을 CSV 파일에 저장

# ==============================
# Streamlit UI
# ==============================

# Streamlit 페이지 UI
def app():
    st.title("상담 AI 테스트")  # Streamlit 앱 제목 설정

    user_question = st.text_area("궁금한 내용을 입력하세요", placeholder="예: 아이오닉5와 아이오닉6 차이점은?", height=150)  # 사용자 질문 입력 영역

    if st.button("답변 생성"):  # 답변 생성 버튼
        if user_question.strip():
            st.info("AI 답변 생성 중...")  # 모델이 답변을 생성 중임을 사용자에게 알림
            result = get_car_info_based_on_question(user_question)  # 모델로부터 답변 가져오기
            st.session_state.generated_answer = result  # 생성된 답변을 세션 상태에 저장
            st.session_state.current_question = user_question  # 현재 질문을 세션 상태에 저장
            st.session_state.generated_tags = extract_tags_from_answer(result)  # 생성된 답변에서 태그 추출
        else:
            st.warning("질문을 입력해주세요.")  # 질문 입력을 사용자에게 경고

    if "generated_answer" in st.session_state and st.session_state.generated_answer:
        st.success("AI 답변 결과")  # 생성된 답변에 대한 성공 메시지 표시
        st.markdown(st.session_state.generated_answer)  # 생성된 답변 표시

        st.markdown("**태그:** " + st.session_state.generated_tags)  # 추출된 태그 표시

        if "오류 발생" not in st.session_state.generated_answer:
            save_to_csv(st.session_state.current_question, st.session_state.generated_answer)  # 질문과 답변을 CSV에 저장
            st.success("질문과 답변이 자동으로 저장되었습니다.")  # 데이터가 저장되었음을 사용자에게 알림
        else:
            st.warning("답변 생성 중 오류가 발생하여 저장되지 않았습니다.")  # 답변 생성 중 오류 발생 시 사용자에게 경고
    
    st.markdown("---")  # 구분선
    st.subheader("이전 질문 및 답변 기록")  # 이전 기록에 대한 서브헤더

    if os.path.exists(LOG_PATH):
        log_df = pd.read_csv(LOG_PATH)  # CSV에서 로그 데이터 읽기
        st.dataframe(log_df, use_container_width=True)  # 데이터프레임으로 로그 데이터 표시
    else:
        st.info("아직 저장된 질문/답변 기록이 없습니다.")  # 저장된 기록이 없음을 사용자에게 알림
