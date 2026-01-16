# 🚗 Hyundai CRM System

현대자동차 고객 관계 관리 및 딜러 지원 통합 플랫폼

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://main-project-codeworks.streamlit.app/)

## 📋 목차

- [프로젝트 개요](#-프로젝트-개요)
- [주요 기능](#-주요-기능)
- [시스템 아키텍처](#-시스템-아키텍처)
- [설치 및 실행](#-설치-및-실행)
- [프로젝트 구조](#-프로젝트-구조)
- [기술 스택](#-기술-스택)
- [데이터 구조](#-데이터-구조)
- [머신러닝 모델](#-머신러닝-모델)
- [개발 가이드](#-개발-가이드)
- [배포](#-배포)

---

## 🎯 프로젝트 개요

Hyundai CRM System은 현대자동차 그룹의 고객 관계 관리, 딜러 지원, 재고 관리 및 판매 분석을 통합한 웹 기반 플랫폼입니다.

### 주요 목표
- **고객 경험 향상**: AI 기반 차량 추천 및 맞춤형 서비스 제공
- **딜러 업무 효율화**: 재고 관리, 수요 예측, 상담 관리 등 통합 대시보드 제공
- **데이터 기반 의사결정**: 판매 분석, 경제 지표 연동, LTV 예측을 통한 전략 수립

---

## ✨ 주요 기능

### 👤 일반 회원 (User Portal)
- **차량 추천**: AI 기반 개인 맞춤형 차량 추천 시스템
- **차량 비교**: 다양한 모델 간 스펙 및 가격 비교
- **카카오 연동**: 카카오 로그인 및 채널 통합
- **상담 신청**: 온라인 상담 예약 및 문의
- **이벤트**: 프로모션 및 이벤트 정보 제공
- **딜러 찾기**: 지도 기반 인근 딜러 검색
- **보조금 조회**: EV 및 수소차 보조금 정보

### 🏪 딜러 허브 (Dealer Hub)
- **대시보드**: 실시간 판매 현황 및 KPI 모니터링
- **재고 관리**: 차량 재고 현황 및 입출고 관리
- **수요 예측**: Prophet 기반 차량 수요 예측
- **상담 관리**: 고객 상담 이력 및 리드 관리
- **판매 등록**: 계약 및 판매 데이터 입력
- **데이터 분석**: 고객 세분화 및 판매 트렌드 분석
- **설문 조사**: 고객 만족도 조사 및 피드백 수집

### 🔧 관리자 콘솔 (Admin Console)
- **판매 분석**
  - 국내/수출 판매 실적 분석
  - 지역별/차종별 성과 분석
  - 목표 대비 달성률 모니터링
  
- **LTV 분석**
  - 고객 생애 가치(LTV) 예측
  - 고객 세그먼트별 분석
  - 시장 트렌드 분석
  
- **마케팅 관리**
  - 캠페인 성과 분석
  - 마케팅 전략 수립
  - ROI 분석
  
- **생산 관리**
  - 공장별 생산량 분석
  - 생산 트렌드 모니터링
  - 생산 보고서 생성
  
- **재고 관리**
  - 전체 재고 현황
  - 재고 회전율 분석
  - 재고 경고 시스템
  
- **경제 지표**
  - Kafka 기반 실시간 경제 데이터 스트리밍
  - GDP, 환율, 금리 등 주요 지표 모니터링
  - 경제 트렌드 분석

- **설정 관리**
  - 사용자 관리
  - 데이터 동기화

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐
│   Home.py       │  ← Entry Point
│   (Routing)     │
└────────┬────────┘
         │
    ┌────┴────────────────────┐
    │                         │
┌───▼────┐  ┌────▼────┐  ┌───▼────┐
│ A_U_   │  │  B_D_   │  │  C_A_  │
│ main   │  │  main   │  │  main  │
│ (User) │  │(Dealer) │  │(Admin) │
└───┬────┘  └────┬────┘  └───┬────┘
    │            │            │
┌───▼────────────▼────────────▼───┐
│       modules/                  │
│  ├─ A_U_*.py (User modules)     │
│  ├─ B_D_*.py (Dealer modules)   │
│  └─ C_A_*.py (Admin modules)    │
└────────────────┬────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼───┐   ┌───▼───┐   ┌───▼───┐
│ data/ │   │model/ │   │Kafka  │
│ (CSV) │   │ (ML)  │   │Stream │
└───────┘   └───────┘   └───────┘
```

### 데이터 흐름
1. **User Input** → Streamlit UI
2. **Data Processing** → Pandas, NumPy
3. **ML Prediction** → XGBoost, LightGBM, Prophet
4. **Visualization** → Plotly, Altair, Matplotlib
5. **Real-time Streaming** → Kafka (경제 지표)

---

## 🚀 설치 및 실행

### 필수 요구사항
- Python 3.8 이상
- pip 패키지 매니저

### 설치 단계

1. **저장소 클론**
```bash
git clone https://github.com/your-repo/main-project.git
cd main-project
```

2. **가상 환경 생성 (권장)**
```bash
python -m venv venv
source venv/bin/activate  # MacOS/Linux
# 또는
venv\Scripts\activate  # Windows
```

3. **패키지 설치**
```bash
pip install -r requirements.txt
```

4. **시스템 종속성 설치 (필요시)**

**MacOS**:
```bash
brew install cmake
brew install font-nanum  # 한글 폰트
```

**Ubuntu/Debian**:
```bash
sudo apt-get install -y python3-dev build-essential cmake
sudo apt-get install -y fonts-nanum*  # 한글 폰트
```

5. **애플리케이션 실행**
```bash
streamlit run Home.py
```

6. **브라우저 접속**
```
http://localhost:8501
```

### 선택적 설치 (얼굴 인식 기능)

```bash
# dlib 설치
pip install cmake==3.26.4
pip install dlib==19.24.2
pip install face_recognition==1.3.0
```

---

## 📁 프로젝트 구조

```
main-project/
│
├── Home.py                    # 메인 진입점 및 라우팅
├── A_U_main.py               # 일반 회원 메인
├── B_D_main.py               # 딜러 메인
├── C_A_main.py               # 관리자 메인
│
├── modules/                   # 모듈 디렉토리
│   ├── A_U_*.py              # 일반 회원 모듈 (12개)
│   ├── B_D_*.py              # 딜러 모듈 (11개)
│   └── C_A_*.py              # 관리자 모듈 (37개)
│
├── data/                      # 데이터 디렉토리
│   ├── customers.csv         # 고객 데이터
│   ├── employee.csv          # 직원 데이터
│   ├── inventory_data.csv    # 재고 데이터
│   ├── car_production.csv    # 생산 데이터
│   ├── car_type.csv          # 차량 정보
│   ├── consult_log.csv       # 상담 이력
│   ├── event.csv             # 이벤트 정보
│   └── processed/            # 전처리된 데이터
│       ├── total/            # 통합 데이터
│       ├── 생산 중/          # 생산 중 차량
│       ├── 생산 종료/        # 단종 차량
│       └── 보조금/           # EV/수소차 보조금
│
├── extra_data/               # 외부 경제 데이터
│   ├── processed/            # 전처리된 경제 지표
│   │   ├── 경제 성장 관련/
│   │   ├── 금융 환경 관련/
│   │   ├── 소비 심리 관련/
│   │   └── 재고 관련/
│   └── raw/                  # 원본 데이터 (XLSX)
│
├── model/                    # 머신러닝 모델
│   ├── xgb_model_*.pkl       # XGBoost 모델들
│   ├── lgb_ltv_model.pkl     # LightGBM 모델
│   ├── cat_ltv_model.pkl     # CatBoost 모델
│   └── *.pkl                 # 기타 학습된 모델
│
├── images/                   # 이미지 리소스
│   ├── hyundai_logo.png
│   ├── user_icon.png
│   ├── shop_icon.png
│   ├── admin_icon.png
│   └── event/                # 이벤트 이미지
│
├── fonts/                    # 한글 폰트
│   └── NanumGothic*          # 나눔고딕 폰트 파일
│
├── jupyter/                  # Jupyter 노트북
│   ├── customer.ipynb        # 고객 분석
│   ├── preprocessing.ipynb   # 데이터 전처리
│   └── *.ipynb              # 기타 분석 노트북
│
├── requirements.txt          # Python 패키지 목록
├── README.md                # 프로젝트 문서 (현재 파일)
└── error_log.txt            # 에러 로그
```

---

## 🛠️ 기술 스택

### Frontend & UI
- **Streamlit** 1.43.0 - 웹 애플리케이션 프레임워크
- **Streamlit JavaScript** - JavaScript 통합
- **Plotly** 5.18.0 - 인터랙티브 차트
- **Altair** - 선언적 시각화
- **Folium** - 지도 시각화
- **Streamlit AgGrid** - 테이블 컴포넌트

### Backend & Data Processing
- **Pandas** 1.5+ - 데이터 처리
- **NumPy** - 수치 연산
- **Python-dateutil** - 날짜 처리
- **Pillow** - 이미지 처리
- **Requests** - HTTP 통신
- **Beautiful Soup 4** - 웹 스크래핑

### Machine Learning
- **Scikit-learn** - ML 알고리즘
- **XGBoost** - Gradient Boosting
- **LightGBM** - 경량 Gradient Boosting
- **CatBoost** - Categorical Boosting
- **Prophet** - 시계열 예측
- **SHAP** - 모델 해석

### Streaming & Real-time
- **Kafka-Python** 2.0.2 - Kafka 클라이언트
- **Confluent-Kafka** 2.2.0 - Kafka 통합

### Visualization & Reporting
- **Matplotlib** - 정적 그래프
- **Seaborn** - 통계 시각화
- **Kaleido** - Plotly 이미지 export
- **ReportLab** - PDF 리포트 생성

### Utilities
- **Geopy** - 지리정보 처리
- **OpenPyXL** - Excel 읽기/쓰기
- **XlsxWriter** - Excel 파일 생성

---

## 📊 데이터 구조

### 주요 데이터셋

| 데이터셋 | 파일명 | 설명 |
|---------|--------|------|
| 고객 정보 | `customers.csv` | 고객 기본 정보 및 프로필 |
| 상담 이력 | `consult_log.csv` | 고객 상담 및 문의 이력 |
| 차량 정보 | `car_type.csv` | 차종별 스펙 및 가격 정보 |
| 재고 데이터 | `inventory_data.csv` | 딜러별 재고 현황 |
| 생산 데이터 | `car_production.csv` | 공장별 생산량 데이터 |
| 직원 정보 | `employee.csv` | 딜러 및 직원 정보 |
| 이벤트 | `event.csv` | 프로모션 및 이벤트 정보 |
| 보조금 | `ev-car.csv`, `hydro-car.csv` | 전기차/수소차 보조금 |

### 외부 경제 데이터
- **GDP/GNI**: 명목/실질 GDP 및 국민총소득
- **환율**: 주요국 통화 대원화 환율
- **금리**: 한국은행 기준금리 및 여수신금리
- **수출입**: 국가별 수출입 데이터
- **소비 심리**: 소비자 심리지수 등 18개 지표

---

## 🤖 머신러닝 모델

### LTV (고객 생애 가치) 예측 모델

| 모델 | 파일명 | 용도 |
|------|--------|------|
| XGBoost | `xgb_domestic_ltv_model.pkl` | 국내 고객 LTV 예측 |
| XGBoost | `xgb_export_ltv_model.pkl` | 수출 고객 LTV 예측 |
| XGBoost | `xgb_DD_ltv_model.pkl` | 딜러 대상 LTV 예측 |
| LightGBM | `lgb_ltv_model.pkl` | 경량 LTV 예측 |
| CatBoost | `cat_ltv_model.pkl` | 범주형 데이터 특화 |

### 기타 모델
- **DecisionTree Model**: 의사결정 트리 기반 분류
- **GradientBoosting Model**: 앙상블 부스팅
- **LightGBM Model**: 고속 그래디언트 부스팅
- **XGBoost Model (v202512111335)**: 최신 버전 통합 모델

### 수요 예측
- **Prophet**: 시계열 기반 차량 수요 예측
- 트렌드, 계절성, 휴일 효과 고려

---

## 💻 개발 가이드

### 모듈 명명 규칙
- `A_U_*.py`: 일반 회원 (User) 모듈
- `B_D_*.py`: 딜러 (Dealer) 모듈  
- `C_A_*.py`: 관리자 (Admin) 모듈

### 페이지 추가 방법

1. **모듈 파일 생성**
```python
# modules/A_U_new_feature.py
import streamlit as st

def app():
    st.title("새로운 기능")
    # 기능 구현
```

2. **메인 파일에 라우팅 추가**
```python
# A_U_main.py
elif page == "new_feature":
    import modules.A_U_new_feature as new_feature
    new_feature.app()
```

### 데이터 로드 패턴
```python
import pandas as pd

# CSV 파일 로드
@st.cache_data
def load_data():
    df = pd.read_csv("data/customers.csv")
    return df

# 사용
df = load_data()
```

### 스타일링 가이드
- **색상**: 현대자동차 브랜드 컬러 사용
- **레이아웃**: `st.columns()` 활용
- **폰트**: 나눔고딕 (한글 지원)
- **아이콘**: `images/` 디렉토리의 PNG 파일

### 로깅
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.info("로그 메시지")
```

---

## 🌐 배포

### Streamlit Cloud 배포

1. **GitHub 저장소 연결**
2. **Streamlit Cloud 설정**
   - Main file: `Home.py`
   - Python version: 3.8+
3. **환경 변수 설정** (필요시)
4. **배포**

**배포 URL**: https://main-project-codeworks.streamlit.app/

### 로컬 배포

```bash
# 프로덕션 모드
streamlit run Home.py --server.port=8501 --server.address=0.0.0.0

# 개발 모드
streamlit run Home.py --server.runOnSave=true
```

---

## 📝 라이선스

이 프로젝트는 현대자동차 그룹의 내부 프로젝트입니다.

---

## 👥 기여

프로젝트 기여는 내부 개발팀을 통해 관리됩니다.

---

## 📞 문의

프로젝트 관련 문의사항은 개발팀에 연락해주세요.

---

## 🔄 버전 히스토리

- **v1.0** (2025-01): 초기 버전 출시
  - 일반 회원, 딜러, 관리자 포털 구축
  - LTV 예측 모델 통합
  - Kafka 기반 실시간 경제 지표 스트리밍
  - Prophet 수요 예측 시스템

---

**Last Updated**: 2026-01-16