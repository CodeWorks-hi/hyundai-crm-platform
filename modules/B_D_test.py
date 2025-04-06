import streamlit as st
import pandas as pd
from huggingface_hub import InferenceClient
import os

TEXT_MODEL_ID = "google/gemma-2-9b-it"
LOG_PATH = "data/qna_log.csv"

# Hugging Face API 토큰 불러오기
def get_huggingface_token(model_type):
    tokens = {"gemma": st.secrets.get("HUGGINGFACE_API_TOKEN_GEMMA")}
    return 'hf_' + tokens.get(model_type)

# 답변 생성 함수
def get_car_info_based_on_question(user_input: str, model_name: str = TEXT_MODEL_ID) -> str:
    token = get_huggingface_token("gemma")
    if not token:
        return "❌ Hugging Face API 토큰이 설정되어 있지 않습니다."

    prompt = f"""
    당신은 현대자동차 차량 추천 및 차량 정보 전문가입니다.

    사용자의 질문에 대해 간결하면서도 구체적인 설명을 제공해주세요.
    질문: {user_input.strip()}
    답변:
    """

    try:
        client = InferenceClient(model=model_name, token=token)
        response = client.text_generation(
            prompt=prompt,
            max_new_tokens=512,
            temperature=0.5,
        )
        return response.strip()
    except Exception as e:
        return f"오류 발생: {e}"

def extract_tags_from_answer(answer: str) -> str:
    tag_prompt = f"""
    다음 설명에서 핵심 키워드를 쉼표로 구분된 태그 형태로 뽑아주세요. 단어 수는 1~2단어로 간결하게 해주세요.

    설명: {answer.strip()}
    태그:
    """
    token = get_huggingface_token("gemma")
    try:
        client = InferenceClient(model=TEXT_MODEL_ID, token=token)
        response = client.text_generation(
            prompt=tag_prompt,
            max_new_tokens=30,
            temperature=0.3,
        )
        return response.strip()
    except Exception as e:
        return "일반"

# CSV 저장 함수
def save_to_csv(question: str, answer: str):
    tag_str = extract_tags_from_answer(answer)

    new_row = pd.DataFrame([{
        "질문": question,
        "답변": answer,
        "답변 태그": tag_str,
        "날짜": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "시간": pd.Timestamp.now().strftime("%H:%M:%S")
    }])

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    if os.path.exists(LOG_PATH):
        df = pd.read_csv(LOG_PATH)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row

    df.to_csv(LOG_PATH, index=False)

# Streamlit 페이지 UI
def app():
    st.title("🔍 차량 관련 AI 질문 도우미")

    user_question = st.text_area("궁금한 내용을 입력하세요", placeholder="예: 아이오닉5와 아이오닉6 차이점은?", height=150)

    if st.button("답변 생성"):
        if user_question.strip():
            st.info("Gemma 모델이 답변을 생성 중입니다...")
            result = get_car_info_based_on_question(user_question)
            st.session_state.generated_answer = result
            st.session_state.current_question = user_question
            st.session_state.generated_tags = extract_tags_from_answer(result)
        else:
            st.warning("질문을 입력해주세요.")

    if "generated_answer" in st.session_state and st.session_state.generated_answer:
        st.success("AI 답변 결과")
        st.markdown(st.session_state.generated_answer)

        st.markdown("**태그:** " + st.session_state.generated_tags)

        if "오류 발생" not in st.session_state.generated_answer:
            save_to_csv(st.session_state.current_question, st.session_state.generated_answer)
            st.success("질문과 답변이 자동으로 저장되었습니다.")
        else:
            st.warning("답변 생성 중 오류가 발생하여 저장되지 않았습니다.")
    
    st.markdown("---")
    st.subheader("📂 이전 질문 및 답변 기록")

    if os.path.exists(LOG_PATH):
        log_df = pd.read_csv(LOG_PATH)
        st.dataframe(log_df, use_container_width=True)
    else:
        st.info("아직 저장된 질문/답변 기록이 없습니다.")