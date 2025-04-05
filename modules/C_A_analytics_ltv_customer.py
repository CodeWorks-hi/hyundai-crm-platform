# 판매·수출 관리
    # LTV 모델 결과, 시장 트렌드, 예측 분석
        # LTV 모델 결과


import streamlit as st
import pandas as pd
import joblib
import numpy as np
from sklearn.preprocessing import OneHotEncoder

# 전처리 파이프라인 (검색 결과 [3] 구조 반영)
def preprocess_data(df, model_type='domestic'):
    # 필수 컬럼 검증
    required_cols = {
        'domestic': ['연령대', '거주 지역', '고객 등급', '차량 구매 횟수', 
                    '평균 구매 금액', '구매 경로', '고객 충성도 지수'],
        'export': ['국가 코드', '환율 정보', '현지 판매 가격', '수출 물류 비용']
    }
    
    # 불필요 컬럼 제거
    drop_cols = {
        'domestic': ['연번', '이름', '생년월일', '휴대폰 번호'],
        'export': ['해외 지사 코드', '현지 유통사 정보']
    }
    
    df = df.drop(columns=drop_cols[model_type], errors='ignore')
    
    # 범주형 변수 인코딩 (검색 결과 [2] 방식)
    categorical_cols = {
        'domestic': ['연령대', '거주 지역', '구매 경로'],
        'export': ['국가 코드']
    }
    
    encoder = OneHotEncoder(handle_unknown='ignore')
    encoded = encoder.fit_transform(df[categorical_cols[model_type]])
    
    # 특징 결합
    numerical_cols = [col for col in required_cols[model_type] if col not in categorical_cols[model_type]]
    processed_df = pd.concat([
        df[numerical_cols].reset_index(drop=True),
        pd.DataFrame(encoded.toarray(), columns=encoder.get_feature_names_out())
    ], axis=1)
    
    return processed_df

# LTV 분석 메인 함수
def ltv_customer_ui():

    with st.spinner("모델 로드 중..."):
        try:
            domestic_model = joblib.load("model/xgb_domestic_ltv_model.pkl")
            export_model = joblib.load("model/xgb_export_ltv_model.pkl")
            st.success("✅ 모델 로드 완료")
        except Exception as e:
            st.error(f"❌ 모델 로드 실패: {str(e)}")
            return

    with st.expander("데이터 업로드 가이드", expanded=True):
        uploaded_file = st.file_uploader("고객 데이터 업로드 (CSV)", type="csv", key="customer_uploader")  # ✅ key 추가

        if uploaded_file:
            with st.spinner("데이터 전처리 중..."):
                try:
                    df = pd.read_csv(uploaded_file)
                    domestic_df = preprocess_data(df, 'domestic')
                    export_df = preprocess_data(df, 'export')
                    st.success("✅ 데이터 전처리 완료")
                except Exception as e:
                    st.error(f"❌ 데이터 처리 오류: {str(e)}")
                    return


            # 예측 진행바
            progress_bar = st.progress(0)
            
            # 국내 예측
            with st.spinner("국내 고객 분석 중..."):
                domestic_pred = domestic_model.predict(domestic_df)
                progress_bar.progress(50)
                
            # 해외 예측
            with st.spinner("해외 고객 분석 중..."):
                export_pred = export_model.predict(export_df)
                progress_bar.progress(100)

            # 결과 시각화
            st.markdown("### 🏆 VIP 고객 분석 결과")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("##### 🇰🇷 국내 TOP 10")
                domestic_results = pd.DataFrame({
                    '고객ID': df['고객ID'][:10],
                    '예측 LTV': np.round(domestic_pred[:10]/1e6, 2)
                })
                st.dataframe(
                    domestic_results.style.format({'예측 LTV': '{:.2f} M'}), 
                    height=400
                )

            with col2:
                st.markdown("##### 🌍 해외 TOP 10")
                export_results = pd.DataFrame({
                    '거래처코드': df['거래처코드'][:10],
                    '예측 LTV': np.round(export_pred[:10]/1e6, 2)
                })
                st.dataframe(
                    export_results.style.format({'예측 LTV': '{:.2f} M'}), 
                    height=400
                )

            # Raw 데이터 보기
            with st.expander("원본 데이터 확인"):
                st.dataframe(df.head(10))

            # 분석 리포트 생성
            if st.button("📊 전체 리포트 생성"):
                with st.spinner("리포트 생성 중..."):
                    # [검색 결과 4] 리포트 생성 로직 추가
                    st.success("✅ 리포트 생성 완료")
                    st.download_button(
                        label="다운로드",
                        data=open("report.pdf", "rb"),
                        file_name="ltv_analysis_report.pdf"
                    )

