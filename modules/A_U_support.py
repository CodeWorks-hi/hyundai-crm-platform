import re
import time
import streamlit as st
from huggingface_hub import InferenceClient


# 모델 설정
TEXT_MODEL_ID = "google/gemma-2-9b-it"

# 📌 Hugging Face API 토큰 가져오기
def get_huggingface_token(model_type):
    tokens = {
        "gemma": st.secrets.get("HUGGINGFACE_API_TOKEN_GEMMA")
    }
    return tokens.get(model_type)

# 📌 사용자 입력 정리
def clean_input(text: str) -> str:
    return re.sub(r"(해줘|알려줘|설명해 줘|말해 줘)", "", text).strip()

# 📌 HTML 태그 제거 (불필요한 경우)
def clean_html_tags(text):
    return re.sub(r'<[^>]+>', '', text)

# 📌 자동차 정보 생성 함수
def get_car_info_based_on_question(user_input: str) -> str:
    token = get_huggingface_token("gemma")
    if not token:
        return "❗ Hugging Face API 토큰이 설정되어 있지 않습니다."

    try:
        # 올바른 클라이언트 초기화 방식
        client = InferenceClient(model=TEXT_MODEL_ID, token=token)




        prompt = f"""
당신은 자동차 전문 상담 AI입니다. 아래 사용자 질문에 대해 친절하고 구체적으로 자동차 정보를 제공하세요.

[사용자 질문]
{user_input}

[답변 지침]
- 구동 방식(전륜/후륜/사륜)의 차이점을 간결하게 설명하세요.
- 트림/옵션별 가격 차이와 장단점을 요약하세요.
- 비교가 필요한 경우 유사 모델과 차이점도 함께 제공하세요.

답변:
"""
        # 생성 요청
        response = client.text_generation(
            prompt=prompt, 
            max_new_tokens=512, 
            temperature=0.7
        )

        return clean_html_tags(response).strip()

    except Exception as e:
        return f"❌ 오류 발생: {str(e)}"

# 🚀 Streamlit UI
def support_ui():
    st.title(" AI 자동차 정보 시스템")

    st.subheader(" 자동차 관련 질문 입력")
    user_question = st.text_area("궁금한 내용을 입력하세요!", placeholder="예: 아이오닉6 트림별 가격 차이는?")

    if st.button("검색하기"):
        if user_question.strip() == "":
            st.warning("❗ 질문을 입력해주세요!")
        else:
            with st.spinner("AI가 답변을 생성 중입니다..."):
                result = get_car_info_based_on_question(clean_input(user_question))
                time.sleep(1.5)

            st.success("✅ 답변이 생성되었습니다!")
            st.subheader("🔍 자동차 정보")
            st.write(result)

