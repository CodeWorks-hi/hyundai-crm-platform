# +---------+
# | 고객 센터  - Google Gemma-2-9B-IT 모델 API 호출|
# +---------+


import json
import re
import os
import time
import streamlit as st
import requests
from huggingface_hub import InferenceClient

TEXT_MODEL_ID = "google/gemma-2-9b-it"

# 📌 Hugging Face API 토큰 가져오기 (`secrets.toml`에서 불러오기)


def get_huggingface_token(model_type):
    tokens = {"gemma": st.secrets.get("HUGGINGFACE_API_TOKEN_GEMMA")}
    return tokens.get(model_type)

def clean_input(text: str) -> str:
    return re.sub(r"(해줘|알려줘|설명해 줘|말해 줘)", "", text).strip()

def clean_html_tags(text):
    return re.sub(r'<[^>]+>', '', text)

def remove_unwanted_phrases(text: str) -> str:
    """
    생성된 결과 텍스트에서 특정 문구(예: '[기타]', '위 내용은 질문에 대한', 
    '보고서 작성을 위해 필요한 정보는 무엇인지요?' 등)를 포함한 줄을 제거
    """
    lines = text.splitlines()
    filtered_lines = []
    for line in lines:
        if "[기타]" in line:
            continue
        if "위 내용은 질문에 대한" in line:
            continue
        # 추가: 보고서 작성을 위한 문구 제거
        if "보고서 작성을 위해 필요한 정보는 무엇인지요?" in line:
            continue
        
        filtered_lines.append(line)
    
    return "\n".join(filtered_lines)

def format_predictions_for_api(predictions):
    if not predictions:
        return {}
    
# 📌 사용자 입력 정리 (불필요한 단어 제거)
def clean_input(text: str) -> str:
    return re.sub(r"\b(해줘|알려줘|설명해 줘|추천해 줘|말해 줘)\b", "", text, flags=re.IGNORECASE).strip()

def generate_text_via_api(prompt: str, predictions: dict, news_items: list, model_name: str = TEXT_MODEL_ID) -> str:
    token = get_huggingface_token("gemma")
    if not token:
        st.error("Hugging Face API 토큰이 없습니다.")
        return ""

    predictions_formatted = format_predictions_for_api(predictions)
    
    system_prompt = """
    [시스템 지시사항]
    ### 1. 분석 요구사항
    - 현대/기아 글로벌 판매 전략 분석
    - 예측 데이터와 최신 뉴스를 종합적으로 고려한 분석
    - 지역별(북미, 유럽, 아시아) 판매 전략 구분 설명
    - 환율 변동이 수출 전략에 미치는 영향 분석
    - 경제 상황에 따른 긍정적/부정적 요인 구분
    - 3가지 시나리오(낙관/중립/비관)로 판매량 예측

    ### 2. 출력 형식
    ## 2025 현대/기아 글로벌 시장 전망 보고서
    | 구분 | 2024 | 2025예상 | 증감률 |
    |------|------|----------|--------|
    | 글로벌 판매량 | X만 대 | Y만 대 | Z% |
    | 주요 시장 점유율 | A% | B% | C%p |

    - 주요 전략:
    - 리스크 요인:
    """

    full_prompt = f"{system_prompt}\n\n[예측 데이터]\n{predictions_formatted}\n\n[사용자 질문]\n{prompt}"
    
    try:
        client = InferenceClient(model=model_name, token=token)
        response = client.text_generation(
            prompt=f"다음 요청에 맞는 분석을 전문가처럼 1000자 내외로 요약해줘:\n{full_prompt}",
            max_new_tokens=1000,
            temperature=0.7
        )
        return response
    except Exception as e:
        st.error(f"텍스트 생성 오류: {e}")
        return ""

    
def gemma_ui():
    st.title("AI 기반 시장 예측 및 분석")
    st.markdown("""
    - 예측 데이터와 최신 뉴스를 종합한 심층 분석 제공
    - 최신 AI 기술을 활용한 시장 동향 예측
    - 데이터 기반의 객관적이고 통찰력 있는 결과 도출
    """)

    if 'predictions' not in st.session_state:
        st.warning("먼저 '예측 시스템' 탭에서 예측을 실행해주세요.")
        return