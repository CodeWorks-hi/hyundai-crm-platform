# 🚗 현대자동차 CRM 통합 플랫폼

### 고객·딜러·관리자를 연결하는 데이터 기반 고객 관계 관리 및 영업 지원 시스템

<div align="center">

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://hyundai-crm-platform-codeworks.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Cloud-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)

</div>

---

## 📖 프로젝트 개요

현대자동차 고객 관계 관리, 딜러 업무 지원, 판매·생산·재고 분석 기능을 하나의 서비스로 통합한 CRM 플랫폼입니다.

고객에게는 차량 추천, 차량 비교, 상담 신청, 이벤트 및 보조금 조회 기능을 제공하고, 딜러에게는 고객 상담 이력, 차량 재고, 판매 실적, 수요 예측 기능을 제공합니다. 관리자는 고객 생애 가치 분석, 마케팅 성과, 생산·재고 현황과 주요 경제 지표를 종합적으로 확인할 수 있습니다.

앞서 개발한 고객 분석 시스템과 ERP 차량 관리 시스템의 데이터와 기능을 확장하여, 고객·딜러·관리자가 각자의 목적에 맞는 서비스를 하나의 Streamlit 애플리케이션에서 이용하도록 구성했습니다.

> 본 프로젝트는 교육 및 포트폴리오 목적으로 제작된 비공식 프로젝트이며, 현대자동차의 공식 서비스나 내부 시스템과는 관련이 없습니다.

---

## 💡 핵심 목표

- 고객 데이터 기반 맞춤형 차량 및 서비스 추천
- 상담·판매·재고 정보를 연결한 딜러 업무 지원
- 고객 생애 가치와 마케팅 성과 분석
- 생산·재고·판매 데이터의 통합 모니터링
- 경제 지표를 활용한 시장 환경 분석
- 사용자 유형별로 분리된 통합 서비스 제공

---

## 🏗️ 시스템 구성

```text
                         Hyundai CRM Platform
                                  │
                     ┌────────────┼────────────┐
                     ▼            ▼            ▼
                일반 고객      딜러 허브     관리자 콘솔
                     │            │            │
          ┌──────────┘            │            └──────────┐
          ▼                       ▼                       ▼
  차량 추천·비교·상담      상담·재고·판매 관리      LTV·마케팅·생산 분석
          │                       │                       │
          └───────────────┬───────┴───────────────┬───────┘
                          ▼                       ▼
                  데이터 처리 계층          머신러닝 계층
                  Pandas · NumPy      XGBoost · LightGBM
                          │            CatBoost · Prophet
                          └───────────┬───────────┘
                                      ▼
                           CSV · 모델 · 외부 데이터
                                      │
                                      ▼
                             경제 지표 데이터 분석
```

---

## 👥 사용자 구성

### 👤 일반 고객

차량 탐색과 상담을 중심으로 한 고객용 서비스를 제공합니다.

- AI 기반 맞춤형 차량 추천
- 차량별 사양 및 가격 비교
- 온라인 상담 신청
- 프로모션 및 이벤트 확인
- 지도 기반 딜러 검색
- 전기차·수소차 보조금 조회
- 카카오 로그인 및 채널 연동

---

### 🏪 딜러

고객 상담과 영업 활동을 지원하는 통합 업무 화면을 제공합니다.

- 판매 현황 및 KPI 대시보드
- 차량 재고 조회 및 입출고 관리
- 고객 상담 이력과 리드 관리
- 계약 및 판매 데이터 등록
- Prophet 기반 차량 수요 예측
- 고객 세분화와 판매 추세 분석
- 고객 만족도 설문 및 피드백 수집

---

### 🔧 관리자

고객·판매·생산·마케팅 정보를 종합적으로 관리합니다.

- 국내 및 해외 판매 실적 분석
- 지역별·차종별 성과 비교
- 목표 대비 판매 달성률 확인
- 고객 생애 가치 분석
- 마케팅 캠페인 성과 및 ROI 분석
- 공장별 생산량과 생산 추세 분석
- 전체 재고와 재고 회전율 모니터링
- 사용자 및 데이터 동기화 관리
- 주요 경제 지표와 시장 흐름 분석

---

## ✨ 주요 기능

### 🚘 AI 기반 차량 추천

고객의 특성과 구매 조건을 분석하여 적합한 차량을 추천합니다.

주요 입력 정보:

- 연령대
- 지역
- 소득 및 예산
- 선호 차종
- 연료 유형
- 과거 구매 및 상담 정보

추천 결과:

- 적합 차량 목록
- 차량별 주요 사양과 가격
- 유사 고객군의 선호 정보
- 관련 이벤트 및 프로모션

---

### 📞 상담 및 고객 관리

고객 상담의 신청부터 이력 관리까지 연결합니다.

- 온라인 상담 신청
- 고객별 상담 이력 조회
- 상담 상태 및 후속 조치 관리
- 관심 차량과 문의 내용 기록
- 고객 리드 관리
- 고객 만족도 및 피드백 수집

---

### 📦 재고 관리

딜러와 관리자가 차량 재고 상태를 확인할 수 있습니다.

- 딜러별 재고 현황
- 차종별 재고 수량
- 차량 입출고 기록
- 재고 회전율 분석
- 부족 및 과잉 재고 탐지
- 재고 경고 표시

---

### 📈 판매 및 생산 분석

판매·생산 데이터를 다각도로 분석합니다.

- 국내 및 해외 판매 비교
- 지역별 판매 실적
- 차종별 판매 비중
- 목표 대비 달성률
- 공장별 생산량
- 생산 및 판매 추세
- 기간별 성과 분석

---

### 🔮 수요 예측

과거 판매 흐름을 바탕으로 미래 차량 수요를 예측합니다.

- Prophet 기반 시계열 분석
- 차종별 수요 예측
- 트렌드와 계절성 반영
- 예측값과 기존 실적 비교
- 딜러 재고 및 판매 전략 지원

---

### 💰 고객 생애 가치 분석

고객의 장기적인 가치를 예측하고 세그먼트별 특성을 분석합니다.

- 국내 고객 LTV 예측
- 해외 고객 LTV 예측
- 딜러 대상 고객 가치 분석
- 고객군별 가치 분포
- 고가치 고객 탐색
- LTV 기반 마케팅 전략 지원

---

### 📢 마케팅 분석

고객과 캠페인 데이터를 기반으로 마케팅 성과를 분석합니다.

- 캠페인별 성과 비교
- 고객군별 반응 분석
- 마케팅 ROI 분석
- 고객 세그먼트별 전략
- 이벤트와 프로모션 관리
- 고객 이탈 방지 전략 지원

---

### 🌐 경제 지표 스트리밍

외부 경제 데이터를 활용하여 시장 환경과 주요 경제 지표를 분석합니다.

주요 지표:

- GDP 및 GNI
- 환율
- 기준금리와 여수신금리
- 수출입 현황
- 소비자 심리지수
- 재고 관련 지표

수집한 경제 지표를 관리자 대시보드에서 시각화하고 시장 분석에 활용하도록 구성했습니다.

---

## 🤖 머신러닝 모델

### 고객 생애 가치 예측

| 모델 | 적용 목적 |
|---|---|
| XGBoost | 국내·해외 및 딜러 고객 LTV 예측 |
| LightGBM | 빠른 학습과 추론을 고려한 LTV 예측 |
| CatBoost | 범주형 변수가 많은 고객 데이터 분석 |

주요 입력 특성:

- 고객 기본 정보
- 구매 금액
- 차량 구매 이력
- 상담 횟수와 상담 내용
- 고객 등급
- 재구매 여부
- 지역 및 시장 구분

---

### 차량 추천 및 고객 분석

적용 모델:

- Decision Tree
- Random Forest
- Gradient Boosting
- LightGBM
- XGBoost

활용 영역:

- 맞춤형 차량 추천
- 고객 세분화
- 구매 가능성 분석
- 고객군별 차량 선호도 분석

---

### 수요 예측

Prophet을 활용하여 시간에 따른 판매량 변화를 분석합니다.

반영 요소:

- 장기 추세
- 계절성
- 기간별 반복 패턴
- 차종별 판매 이력
- 시장 변화

---

### 모델 해석

SHAP을 활용해 예측에 영향을 준 주요 특성을 확인할 수 있도록 구성했습니다.

- 고객 특성별 영향도 분석
- LTV 예측 근거 확인
- 모델 변수 중요도 비교
- 마케팅 및 상담 전략 수립 지원

---

## 📊 데이터 흐름

```text
고객·상담·차량·재고·판매 데이터
                │
                ▼
       데이터 정제 및 통합
                │
                ▼
     고객·딜러·관리자 목적별 가공
                │
        ┌───────┼────────┐
        ▼       ▼        ▼
    고객 분석  재고 분석  판매·생산 분석
        │       │        │
        └───────┼────────┘
                ▼
       머신러닝 및 시계열 예측
                │
                ▼
     추천·LTV·수요 예측 결과 생성
                │
                ▼
      역할별 Streamlit 화면 제공
```

---

## 🗂️ 데이터 구성

| 데이터 | 파일 | 주요 내용 |
|---|---|---|
| 고객 데이터 | `customers.csv` | 고객 기본 정보와 구매 이력 |
| 상담 데이터 | `consult_log.csv` | 상담 내용, 상태 및 이력 |
| 차량 데이터 | `car_type.csv` | 차량 사양, 가격 및 연료 유형 |
| 재고 데이터 | `inventory_data.csv` | 딜러별·차종별 재고 현황 |
| 생산 데이터 | `car_production.csv` | 공장 및 차종별 생산량 |
| 직원 데이터 | `employee.csv` | 딜러와 관리자 정보 |
| 이벤트 데이터 | `event.csv` | 프로모션 및 이벤트 정보 |
| 보조금 데이터 | `ev-car.csv`, `hydro-car.csv` | 친환경 차량 보조금 정보 |

### 외부 경제 데이터

- 경제 성장 지표
- 금융 환경 지표
- 소비 심리 지표
- 환율 및 금리
- 수출입 데이터
- 재고 및 판매 관련 지표

---

## ⚙️ 기술 스택

### Application & UI

<p>

  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white"/>
  <img src="https://img.shields.io/badge/Altair-FD4B4B?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Folium-77B829?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/AgGrid-0088CC?style=for-the-badge"/>

</p>

### Data Processing

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
  <img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white"/>
  <img src="https://img.shields.io/badge/BeautifulSoup-59666C?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/OpenPyXL-217346?style=for-the-badge"/>
</p>

### Machine Learning

<p>
  <img src="https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white"/>
  <img src="https://img.shields.io/badge/XGBoost-EC6B23?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/LightGBM-017CEE?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/CatBoost-FFCC00?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Prophet-0072B5?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/SHAP-5A45FF?style=for-the-badge"/>
</p>

### External Services

<p>
  <img src="https://img.shields.io/badge/Kakao-FFCD00?style=for-the-badge&logo=kakao&logoColor=black"/>
</p>

### Reporting & Deployment

<p>
  <img src="https://img.shields.io/badge/Streamlit%20Cloud-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/ReportLab-CC0000?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Excel-217346?style=for-the-badge&logo=microsoftexcel&logoColor=white"/>
</p>

---

## 📂 프로젝트 구조

```text
hyundai-crm-platform/
├── Home.py
├── A_U_main.py
├── B_D_main.py
├── C_A_main.py
├── modules/
│   ├── A_U_*.py
│   ├── B_D_*.py
│   └── C_A_*.py
├── data/
│   ├── customers.csv
│   ├── employee.csv
│   ├── inventory_data.csv
│   ├── car_production.csv
│   ├── car_type.csv
│   ├── consult_log.csv
│   ├── event.csv
│   └── processed/
├── extra_data/
│   ├── raw/
│   └── processed/
├── model/
│   ├── xgb_model_*.pkl
│   ├── xgb_domestic_ltv_model.pkl
│   ├── xgb_export_ltv_model.pkl
│   ├── xgb_DD_ltv_model.pkl
│   ├── lgb_ltv_model.pkl
│   └── cat_ltv_model.pkl
├── images/
├── fonts/
├── jupyter/
├── requirements.txt
└── README.md
```

### 모듈 명명 규칙

| 접두어 | 사용자 영역 |
|---|---|
| `A_U_` | 일반 고객 |
| `B_D_` | 딜러 |
| `C_A_` | 관리자 |

---

## 🚀 설치 및 실행

### 1. 저장소 클론

```bash
git clone https://github.com/CodeWorks-hi/hyundai-crm-platform.git
cd hyundai-crm-platform
```

### 2. 가상환경 생성

```bash
python -m venv venv
```

macOS / Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 3. 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 4. 애플리케이션 실행

```bash
streamlit run Home.py
```

실행 후 브라우저에서 아래 주소로 접속합니다.

```text
http://localhost:8501
```

---

## 🌐 온라인 데모

[Streamlit 애플리케이션 바로가기](https://hyundai-crm-platform-codeworks.streamlit.app/)

---

## 📌 프로젝트 특징

- 고객·딜러·관리자를 구분한 역할 기반 서비스
- 고객 분석 시스템과 ERP 플랫폼 기능의 통합
- 차량 추천, LTV 분석, 수요 예측을 결합한 머신러닝 서비스
- 상담·판매·재고·생산 데이터를 연결한 CRM 구조
- 외부 경제 지표를 활용한 시장 분석
- Plotly·Altair·Folium을 활용한 대화형 시각화
- CSV·Excel·PDF 형태의 데이터 및 리포트 활용
- Streamlit 기반의 통합 업무·고객 서비스 구현

---

## 📝 안내

본 프로젝트는 교육 및 포트폴리오 목적으로 제작된 비공식 프로젝트입니다.

현대자동차의 공식 서비스, 내부 CRM, 운영 데이터 또는 실제 딜러 시스템과는 관련이 없습니다.
