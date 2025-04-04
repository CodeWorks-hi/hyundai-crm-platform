import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sb

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

    # 선택 연도
    years = sorted(df_customer['최근 구매 연도'].unique())
    default_year = 2024
    if default_year in years:
        default_index = years.index(default_year)
    else:
        default_index = len(years) - 1
    year = st.selectbox("📅 연도 선택", years, index=default_index)

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
    st.markdown("### 📊 주요 지표")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 고객 수", f"{total_customers} 명")
    col2.metric("평균 연령", f"{avg_age:.1f} 세")
    col3.metric("전년대비 판매 증가율", f"{YoY_growth}%")
    col4.metric("총 판매량", f"{total_sales} 대")

    # 분포 시각화 (깔끔한 레이아웃)
    st.markdown("---")
    st.markdown("### 🎨 고객 분포 시각화")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**연령대 분포**")
        age_counts = df_filtered['연령대'].value_counts()
        fig, ax = plt.subplots()
        colors = plt.cm.Set3.colors[:len(age_counts)]  # 고유한 옅은 색상 사용 (Set3 팔레트)
        ax.pie(age_counts, colors=colors, startangle=90)
        ax.legend(sorted(age_counts.index), title="연령대", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        st.pyplot(fig)

    with col2:
        st.write("**고객 그룹 분포**")
        group_counts = df_filtered['고객 그룹'].value_counts()
        fig, ax = plt.subplots()
        colors = plt.cm.Set3.colors[:len(group_counts)]  # 고유한 옅은 색상 사용 (Set3 팔레트)
        ax.pie(group_counts, colors=colors, startangle=90)
        ax.legend(sorted(group_counts.index), title="고객 그룹", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        st.pyplot(fig)

    with col3:
        st.write("**거주 지역 분포**")
        region_counts = df_filtered['거주 지역'].value_counts()
        fig, ax = plt.subplots()
        colors = plt.cm.Set3.colors[:len(region_counts)]  # 고유한 색상 사용
        ax.bar(region_counts.index, region_counts.values, color=colors)
        ax.set_title("거주 지역별 고객 수")
        ax.set_xlabel("거주 지역")
        ax.set_ylabel("고객 수")
        plt.xticks(rotation=45)  # 지역명이 길 경우 회전
        st.pyplot(fig)


    # 판매된 모델 및 구매 트렌드 시각화
    st.markdown("---")
    st.markdown("### 🚘 판매된 모델 및 구매 트렌드")

    col1, col2 = st.columns(2)

    with col1:
        # 연령대 통합 (20대, 30대 등으로 묶음)
        df_filtered['통합 연령대'] = df_filtered['연령대'].replace(
            {
                '20대 초반': '20대', '20대 중반': '20대', '20대 후반': '20대',
                '30대 초반': '30대', '30대 중반': '30대', '30대 후반': '30대',
                '40대 초반': '40대', '40대 중반': '40대', '40대 후반': '40대',
                '50대 초반': '50대', '50대 중반': '50대', '50대 후반': '50대',
                '60대 초반': '60대 이상', '60대 중반': '60대 이상', 
                '60대 후반': '60대 이상', '70대 초반': '60대 이상'
            }
        )

        # Streamlit UI: 연령대 선택
        age_options = df_filtered['통합 연령대'].unique()  # 고유한 통합 연령대를 가져옴
        age_choice = st.selectbox('연령대를 선택하세요:', sorted(age_options))  # 사용자 인터페이스 생성

        # 선택한 연령대로 데이터 필터링
        filtered_data = df_filtered[df_filtered['통합 연령대'] == age_choice]

        # 차량 모델별 구매 수 계산
        model_counts = filtered_data['최근 구매 제품'].value_counts()

        # 원형 차트 그리기 (크기 조정)
        fig, ax = plt.subplots(figsize=(4, 4))  # 그래프 크기를 4x4로 설정
        colors = plt.cm.Set3.colors[:len(model_counts)]  # 색상 설정
        ax.pie(model_counts, colors=colors)
        ax.set_title(f"{age_choice} 구매 차량 모델 분포", fontsize=10)
        ax.legend(sorted(model_counts.index), title="차량 모델", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        st.pyplot(fig)



    with col2:
        trend_options = ['월별', '분기별', '요일별', '계절별']
        trend_choice = st.selectbox('구매 트렌드 선택', trend_options)

        if not pd.api.types.is_datetime64_any_dtype(df_filtered['최근 구매 날짜']):
            df_filtered['최근 구매 날짜'] = pd.to_datetime(df_filtered['최근 구매 날짜'], errors='coerce')

        if trend_choice == '월별':
            monthly_sales = df_filtered.groupby(df_filtered['최근 구매 날짜'].dt.strftime('%Y-%m'))['아이디'].count()
            fig, ax = plt.subplots(figsize=(6, 4))  # 그래프 크기를 6x4로 설정
            ax.plot(monthly_sales.index, monthly_sales.values, marker='o', linestyle='-', color=plt.cm.Set3.colors[0])
            ax.set_title("월별 구매 트렌드", fontsize=10)
            ax.set_xlabel("월")
            ax.set_ylabel("판매량")
            plt.xticks(rotation=45)
            st.pyplot(fig)

        elif trend_choice == '분기별':
            df_filtered['분기'] = df_filtered['최근 구매 날짜'].dt.quarter
            fig, ax = plt.subplots(figsize=(6, 4))  # 그래프 크기를 6x4로 설정
            sb.countplot(data=df_filtered, x='분기', palette=ListedColormap(plt.cm.Set3.colors).colors[:4], ax=ax)
            ax.set_title('분기별 고객 수', fontsize=10)
            ax.set_xlabel('분기')
            ax.set_ylabel('고객 수')
            plt.xticks(rotation=45)
            st.pyplot(fig)

        elif trend_choice == '요일별':
            df_filtered['요일'] = df_filtered['최근 구매 날짜'].dt.day_name()
            weekday_sales = df_filtered.groupby('요일')['아이디'].count()
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_sales = weekday_sales.reindex(weekday_order)
            fig, ax = plt.subplots(figsize=(6, 4))  # 그래프 크기를 6x4로 설정
            ax.bar(weekday_sales.index, weekday_sales.values, color=plt.cm.Set3.colors[:7])
            ax.set_title("요일별 구매 트렌드", fontsize=10)
            ax.set_xlabel("요일")
            ax.set_ylabel("판매량")
            st.pyplot(fig)

        elif trend_choice == '계절별':
            def get_season(month):
                if month in [12, 1, 2]:
                    return "겨울"
                elif month in [3, 4, 5]:
                    return "봄"
                elif month in [6, 7, 8]:
                    return "여름"
                else:
                    return "가을"

            df_filtered['계절'] = df_filtered['최근 구매 날짜'].dt.month.apply(get_season)
            season_sales = df_filtered.groupby('계절')['아이디'].count()
            season_order = ['봄', '여름', '가을', '겨울']
            season_sales = season_sales.reindex(season_order)
            fig, ax = plt.subplots(figsize=(6, 4))  # 그래프 크기를 6x4로 설정
            ax.bar(season_sales.index, season_sales.values, color=plt.cm.Set3.colors[:4])
            ax.set_title("계절별 구매 트렌드", fontsize=10)
            ax.set_xlabel("계절")
            ax.set_ylabel("판매량")
            st.pyplot(fig)
