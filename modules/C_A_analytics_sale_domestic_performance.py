import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sb
from matplotlib import font_manager, rc
import matplotlib.pyplot as plt
import os
import platform


# 한글 폰트 설정 함수
def set_korean_font():
    try:
        if platform.system() == "Darwin":  # macOS
            rc("font", family="AppleGothic")
        elif platform.system() == "Windows":
            font_path = "C:/Windows/Fonts/malgun.ttf"
            if os.path.exists(font_path):
                font_name = font_manager.FontProperties(fname=font_path).get_name()
                rc("font", family=font_name)
        elif platform.system() == "Linux":
            font_path = "fonts/NanumGothic.ttf"
            if os.path.exists(font_path):
                font_manager.fontManager.addfont(font_path)
                font_name = font_manager.FontProperties(fname=font_path).get_name()
                rc("font", family=font_name)
            else:
                st.error("Linux 환경에서 NanumGothic.ttf 폰트가 없습니다. 'fonts' 폴더에 추가해주세요.")
    except Exception as e:
        st.warning(f"폰트 설정 중 오류 발생: {e}")
    plt.rcParams["axes.unicode_minus"] = False

# 호출
set_korean_font()

# 데이터 경로 설정
car_list_path = "data/hyundae_car_list.csv"
inventory_path = "data/inventory_data.csv"
customer_path = "data/customer_data.csv"

# 데이터 로드
df_inv = pd.read_csv(inventory_path)
df_list = pd.read_csv(car_list_path)
df_customer = pd.read_csv(customer_path)

def domestic_performance_ui():
    st.title("🚗 국내 판매 실적 분석")
    st.write("고객 구매 실적 및 주요 통계를 한눈에 확인하세요.")

    df_customer['통합 연령대'] = df_customer['연령대'].replace(
            {
                '20대 초반': '20대', '20대 중반': '20대', '20대 후반': '20대',
                '30대 초반': '30대', '30대 중반': '30대', '30대 후반': '30대',
                '40대 초반': '40대', '40대 중반': '40대', '40대 후반': '40대',
                '50대 초반': '50대', '50대 중반': '50대', '50대 후반': '50대',
                '60대 초반': '60대 이상', '60대 중반': '60대 이상', 
                '60대 후반': '60대 이상', '70대 초반': '60대 이상'
            }
        )

    # 선택 연도
    years = sorted(df_customer['최근 구매 연도'].unique())
    default_year = 2024
    if default_year in years:
        default_index = years.index(default_year)
    else:
        default_index = len(years) - 1
    year = st.selectbox(" 연도 선택", years, index=default_index)

    # 데이터 필터링
    df_filtered = df_customer[df_customer['최근 구매 연도'] == year]

    # 주요 지표 계산
    total_customers = df_filtered['아이디'].nunique()
    avg_age = df_filtered['현재 나이'].mean()
    total_sales = len(df_filtered)

    # 전년대비 판매 증가율 계산
    if year - 1 in years:
        last_year_sales = len(df_customer[df_customer['최근 구매 연도'] == year - 1])
        YoY_growth = round(((total_sales - last_year_sales) / last_year_sales) * 100, 2) if last_year_sales > 0 else "-"
    else:
        YoY_growth = "-"
        

    # 주요 지표 표시 (카드 스타일)
    st.markdown("###  주요 지표")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 고객 수", f"{total_customers} 명")
    col2.metric("평균 연령", f"{avg_age:.1f} 세")
    col3.metric("전년대비 판매 증가율", f"{YoY_growth}%")
    col4.metric("총 판매량", f"{total_sales} 대")


    # 분포 시각화 (깔끔한 레이아웃)
    st.markdown("---")
    st.markdown("### 고객 분포 시각화")
    
    col1, col2 = st.columns(2)

    with col1:
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            # 연령대 선택 셀렉박스 (전체 옵션 포함)
            age_options = sorted(df_customer['통합 연령대'].unique().tolist())
            selected_age = st.selectbox("연령대 선택", options=['전체'] + age_options, index=0)
        with col1_2:
            # 성별 선택 셀렉박스 (전체 옵션 포함)
            gender_options = df_customer['성별'].unique().tolist()
            selected_gender = st.selectbox("성별 선택", options=['전체'] + gender_options, index=0)

        # 필터링 로직 수정
        if selected_age == '전체' and selected_gender == '전체':
            df_filtered = df_customer.copy()  # 전체 데이터 사용
            chart_data = df_filtered['통합 연령대'].value_counts()
            legend_title = "연령대"  # 범례 제목 설정 (연령대 기준)
        elif selected_age == '전체':
            df_filtered = df_customer[df_customer['성별'] == selected_gender]  # 성별만 필터링
            chart_data = df_filtered['통합 연령대'].value_counts()
            legend_title = "연령대"  # 범례 제목 설정 (연령대 기준)
        elif selected_gender == '전체':
            df_filtered = df_customer[df_customer['통합 연령대'] == selected_age]  # 연령대만 필터링
            chart_data = df_filtered['성별'].value_counts()
            legend_title = "성별"  # 범례 제목 설정 (성별 기준)
        else:
            df_filtered = df_customer[(df_customer['통합 연령대'] == selected_age) & (df_customer['성별'] == selected_gender)]  # 연령대와 성별 모두 필터링
            chart_data = df_filtered['성별'].value_counts()
            legend_title = "성별"  # 범례 제목 설정 (성별 기준)

        # 데이터가 없는 경우 처리
        if chart_data.empty:
            st.write("필터링된 데이터가 없습니다.")
        else:
            st.write("**연령대/성별 분포**")
            fig, ax = plt.subplots(figsize=(6, 6))  # 그래프 크기 설정
            colors = plt.cm.Set3.colors[:len(chart_data)]  # 고유한 옅은 색상 사용 (Set3 팔레트)
            ax.pie(chart_data, colors=colors, startangle=90)  # 비율 표시 추가
            ax.legend(sorted(chart_data.index), title=legend_title, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            st.pyplot(fig)

    with col2:
        col1, col2 = st.columns(2)
        with col1:
            # 연령대 선택 셀렉박스 (전체 옵션 포함) - 고유 키 추가
            age_options = sorted(df_customer['통합 연령대'].unique().tolist())
            selected_age = st.selectbox("연령대 선택", options=['전체'] + age_options, index=0, key="age_selectbox")
        with col2:
            # 성별 선택 셀렉박스 (전체 옵션 포함) - 고유 키 추가
            gender_options = df_customer['성별'].unique().tolist()
            selected_gender = st.selectbox("성별 선택", options=['전체'] + gender_options, index=0, key="gender_selectbox")

        # 필터링 로직
        if selected_age == '전체' and selected_gender == '전체':
            df_filtered = df_customer.copy()  # 필터링 해제
        elif selected_age == '전체':
            df_filtered = df_customer[df_customer['성별'] == selected_gender]  # 성별만 필터링
        elif selected_gender == '전체':
            df_filtered = df_customer[df_customer['통합 연령대'] == selected_age]  # 연령대만 필터링
        else:
            df_filtered = df_customer[(df_customer['통합 연령대'] == selected_age) & (df_customer['성별'] == selected_gender)]  # 연령대와 성별 모두 필터링

        # 차량 모델별 구매 수량 계산
        model_counts = df_filtered['최근 구매 제품'].value_counts()

        # 시각화 데이터 준비
        if model_counts.empty:
            st.write("필터링된 데이터가 없습니다.")
        else:
            st.write("**선택된 조건에 따른 차량 모델 구매 비율**")
            
            # 원형 차트 시각화
            fig, ax = plt.subplots(figsize=(6, 6))
            colors = plt.cm.Set3.colors[:len(model_counts)]  # 고유한 색상 사용 (Set3 팔레트)
            ax.pie(model_counts, startangle=90, colors=colors)
            ax.legend(sorted(model_counts.index), title=legend_title, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            st.pyplot(fig)

    st.markdown("---")

    # 등급별 구매 모델 비율
    st.markdown("### 등급별 구매 모델 비율")

    col1, col2 = st.columns(2)

    with col1:
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            # 연령대 선택 셀렉박스 (전체 옵션 포함) - 고유 키 추가
            age_options = sorted(df_customer['통합 연령대'].unique().tolist())
            selected_age = st.selectbox("연령대 선택", options=['전체'] + age_options, index=0, key="age_selectbox_1")
        with col1_2:
            # 성별 선택 셀렉박스 (전체 옵션 포함) - 고유 키 추가
            gender_options = df_customer['성별'].unique().tolist()
            selected_gender = st.selectbox("성별 선택", options=['전체'] + gender_options, index=0, key="gender_selectbox_1")
        
        # 필터링 로직
        if selected_age == '전체' and selected_gender == '전체':
            df_filtered = df_customer.copy()  # 필터링 해제
        elif selected_age == '전체':
            df_filtered = df_customer[df_customer['성별'] == selected_gender]  # 성별만 필터링
        elif selected_gender == '전체':
            df_filtered = df_customer[df_customer['통합 연령대'] == selected_age]  # 연령대만 필터링
        else:
            df_filtered = df_customer[(df_customer['통합 연령대'] == selected_age) & (df_customer['성별'] == selected_gender)]  # 연령대와 성별 모두 필터링
        
        # 등급 별 분포
        grade_counts = df_filtered['고객 그룹'].value_counts()
        
        # 시각화 데이터 준비
        if grade_counts.empty:
            st.write("필터링된 데이터가 없습니다.")
        else:
            st.write("**선택된 조건에 따른 구매 모델 분포**")
            
            # 원형 차트 시각화
            fig, ax = plt.subplots(figsize=(6, 6))
            colors = plt.cm.Set3.colors[:len(grade_counts)]  # 색상 팔레트 설정
            
            ax.pie(grade_counts, startangle=90, colors=colors)
            
            ax.legend(sorted(grade_counts.index),title="고객 그룹", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            st.pyplot(fig)

    with col2:
        col1, col2,col3 = st.columns(3)
        with col1:
            # 등급 선택 셀렉박스 (전체 옵션 포함) - 고유 키 추가
            grade_options = sorted(df_customer['고객 그룹'].unique().tolist())
            selected_grade = st.selectbox("등급 선택", options=['전체'] + grade_options, index=0, key="grade_selectbox")
        with col2:
            # 연령대 선택 셀렉박스 (전체 옵션 포함) - 고유 키 추가
            age_options = sorted(df_customer['통합 연령대'].unique().tolist())
            selected_age = st.selectbox("연령대 선택", options=['전체'] + age_options, index=0, key="age_selectbox_2")
        with col3:
            # 성별 선택 셀렉박스 (전체 옵션 포함) - 고유 키 추가
            gender_options = df_customer['성별'].unique().tolist()
            selected_gender = st.selectbox("성별 선택", options=['전체'] + gender_options, index=0, key="gender_selectbox_2")
        
        # 필터링 로직
        if selected_grade == '전체' and selected_age == '전체' and selected_gender == '전체':
            df_filtered = df_customer.copy()  # 모든 데이터 사용
        elif selected_grade == '전체' and selected_age == '전체':
            df_filtered = df_customer[df_customer['성별'] == selected_gender]  # 성별만 필터링
        elif selected_grade == '전체' and selected_gender == '전체':
            df_filtered = df_customer[df_customer['통합 연령대'] == selected_age]  # 연령대만 필터링
        elif selected_age == '전체' and selected_gender == '전체':
            df_filtered = df_customer[df_customer['고객 그룹'] == selected_grade]  # 등급만 필터링
        elif selected_grade == '전체':
            df_filtered = df_customer[(df_customer['통합 연령대'] == selected_age) & (df_customer['성별'] == selected_gender)]  # 연령대와 성별 필터링
        elif selected_age == '전체':
            df_filtered = df_customer[(df_customer['고객 그룹'] == selected_grade) & (df_customer['성별'] == selected_gender)]  # 등급과 성별 필터링
        elif selected_gender == '전체':
            df_filtered = df_customer[(df_customer['고객 그룹'] == selected_grade) & (df_customer['통합 연령대'] == selected_age)]  # 등급과 연령대 필터링
        else:
            df_filtered = df_customer[(df_customer['고객 그룹'] == selected_grade) & 
                                    (df_customer['통합 연령대'] == selected_age) & 
                                    (df_customer['성별'] == selected_gender)]
        # 차량 모델별 구매 수량 계산
        model_counts = df_filtered['최근 구매 제품'].value_counts()
        # 시각화 데이터 준비
        if model_counts.empty:
            st.write("필터링된 데이터가 없습니다.")
        else:
            st.write("**선택된 조건에 따른 차량 모델 구매 비율**")
            
            # 원형 차트 시각화
            fig, ax = plt.subplots(figsize=(6, 6))
            colors = plt.cm.Set3.colors[:len(model_counts)]
            # 고유한 색상 사용 (Set3 팔레트)
            ax.pie(model_counts, startangle=90, colors=colors)
            ax.legend(sorted(model_counts.index), title="차량 모델", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            st.pyplot(fig)
        
    st.markdown("---")

    # 구매 트렌드
    st.markdown("### 구매 트렌드")
    col1, col2 = st.columns(2)
    
    with col1:
        # 트렌드 셀렉 박스 (고유 키 추가)
        trend_options = ['분기', '월', '요일', '계절']
        selected_trend = st.selectbox(
            "트렌드 선택", 
            trend_options, 
            index=0,
            key="unique_trend_selectbox"  # 고유 키 지정
        )

        # 트렌드 데이터 준비
        if selected_trend == '분기':
            df_filtered['구매 분기'] = pd.to_datetime(df_filtered['최근 구매 날짜']).dt.to_period('Q').astype(str)
            trend_data = df_filtered.groupby('구매 분기')['아이디'].nunique()
        elif selected_trend == '월':
            df_filtered['구매 월'] = pd.to_datetime(df_filtered['최근 구매 날짜']).dt.month
            trend_data = df_filtered.groupby('구매 월')['아이디'].nunique()
        elif selected_trend == '요일':
            df_filtered['구매 요일'] = pd.to_datetime(df_filtered['최근 구매 날짜']).dt.day_name(locale='ko_KR.UTF-8')  # 한국어 요일
            days_order = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
            trend_data = df_filtered.groupby('구매 요일')['아이디'].nunique().reindex(days_order, fill_value=0)
        elif selected_trend == '계절':
            df_filtered['구매 시즌'] = pd.to_datetime(df_filtered['최근 구매 날짜']).dt.month % 12 // 3 + 1
            season_map = {1: '봄', 2: '여름', 3: '가을', 4: '겨울'}
            df_filtered['구매 시즌'] = df_filtered['구매 시즌'].map(season_map)
            trend_data = df_filtered.groupby('구매 시즌')['아이디'].nunique()

        # 시각화 데이터 준비
        if trend_data.empty:
            st.write("필터링된 데이터가 없습니다.")
        else:
            st.write(f"**{selected_trend}별 구매 트렌드**")
            
            # 라인 차트 시각화
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(trend_data.index, trend_data.values, marker='o', linestyle='-', color='skyblue')
            
            # 레이블 설정
            ax.set_xlabel(selected_trend, fontsize=12)
            ax.set_ylabel("구매 고객 수", fontsize=12)
            ax.set_title(f"{selected_trend}별 구매 트렌드", fontsize=14)
            plt.xticks(rotation=45)  # x축 레이블 회전 (가독성 향상)
            ax.grid(True, linestyle='--', alpha=0.7)
            
            st.pyplot(fig)

    with col2:
        # 차량 모델별 구매 트렌드
        trend_options = ['분기', '월', '요일', '계절']
        selected_trend = st.selectbox(
            "트렌드 선택", 
            trend_options, 
            index=0,
            key="unique_trend_selectbox_1"  # 고유 키 지정
        )
        # 트렌드 데이터 준비
        if selected_trend == '분기':
            df_filtered['구매 분기'] = pd.to_datetime(df_filtered['최근 구매 날짜']).dt.to_period('Q').astype(str)
            trend_data = df_filtered.groupby(['구매 분기', '최근 구매 제품']).size().unstack(fill_value=0)
        elif selected_trend == '월':
            df_filtered['구매 월'] = pd.to_datetime(df_filtered['최근 구매 날짜']).dt.month
            trend_data = df_filtered.groupby(['구매 월', '최근 구매 제품']).size().unstack(fill_value=0)
        elif selected_trend == '요일':
            df_filtered['구매 요일'] = pd.to_datetime(df_filtered['최근 구매 날짜']).dt.day_name(locale='ko_KR.UTF-8')
            days_order = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
            trend_data = df_filtered.groupby(['구매 요일', '최근 구매 제품']).size().unstack(fill_value=0).reindex(days_order)
        elif selected_trend == '계절':
            df_filtered['구매 시즌'] = pd.to_datetime(df_filtered['최근 구매 날짜']).dt.month % 12 // 3 + 1
            season_map = {1: '봄', 2: '여름', 3: '가을', 4: '겨울'}
            df_filtered['구매 시즌'] = df_filtered['구매 시즌'].map(season_map)
            trend_data = df_filtered.groupby(['구매 시즌', '최근 구매 제품']).size().unstack(fill_value=0)

        # 시각화 데이터 준비
        if trend_data.empty:
            st.write("필터링된 데이터가 없습니다.")
        else:
            st.write(f"**{selected_trend}별 차량 모델 구매 트렌드**")
            
            # 선택된 트렌드에 따라 특정 기간의 데이터를 합산
            aggregated_data = trend_data.sum(axis=0)  # 모든 기간 합산 (열 기준)
            
            # 원형 차트 시각화
            fig, ax = plt.subplots(figsize=(5, 5))
            colors = plt.cm.Set3.colors[:len(aggregated_data)]
            
            ax.pie(aggregated_data, startangle=90, colors=colors)
            ax.legend(aggregated_data.index, title="차량 모델", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            st.pyplot(fig)

    # 원본데이터 보기
    with st.expander("원본 데이터 보기", expanded=False):
            st.write(df_filtered)
            st.dataframe(df_filtered, use_container_width=True)
