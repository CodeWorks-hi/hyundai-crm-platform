

# +------------+
# | 모델 상세보기 |
# +------------+

import streamlit as st
import pandas as pd
import os
st.write("✅ A_U_detail.py 진입 성공")

if not os.path.exists("data/selected_car.csv"):
    st.error("❌ selected_car.csv 파일이 없습니다.")
    st.stop()

df_sel = pd.read_csv("data/selected_car.csv")
st.write("✔ 선택된 차량 정보:", df_sel)

try:
    selected_model = df_sel.iloc[0]["선택모델"]
except Exception as e:
    st.error(f"🚫 선택모델 읽기 실패: {e}")
    st.stop()

df = pd.read_csv("data/hyundae_car_list.csv")
st.write("✔ 차량 전체 데이터 개수:", len(df))

filtered = df[df["모델명"] == selected_model]
st.write("🔍 선택된 모델:", selected_model)
st.write("📊 필터링된 데이터 수:", len(filtered))

if filtered.empty:
    st.warning("⚠ 선택한 모델명에 해당하는 차량이 없습니다.")
    st.stop()


def detail_ui():
    st.set_page_config(page_title="차량 상세 보기", layout="wide")

    # 선택된 차량 불러오기
    try:
        selected_model = pd.read_csv("data/selected_car.csv").iloc[0]["선택모델"]
    except Exception as e:
        st.error("선택된 차량 정보가 없습니다.\n차량을 먼저 선택해 주세요.")
        return

    # 차량 전체 리스트에서 해당 모델명으로 필터링
    try:
        df = pd.read_csv("data/hyundae_car_list.csv")
    except FileNotFoundError:
        st.error("차량 데이터 파일이 존재하지 않습니다.")
        return

    filtered = df[df["모델명"] == selected_model]

    if filtered.empty:
        st.warning(f"'{selected_model}'에 해당하는 차량이 없습니다.")
        return

    st.title(f" {selected_model} 전체 트림 보기")
    st.markdown("---")

    for idx, row in filtered.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 2])

            with col1:
                st.image(row["img_url"], width=250)

            with col2:
                st.subheader(f"{row['트림명']} | {int(row['기본가격']):,}원")
                st.markdown(f"""
                - **모델 구분**: {row['모델 구분']}
                - **탑승 인원**: {row['탑승인원']}
                - **연료 구분**: {row['연료구분']}
                - **차량 형태**: {row['차량형태']}
                - **전장/전폭/전고**: {row['전장']} × {row['전폭']} × {row['전고']} mm
                - **공차중량**: {row['공차중량']} kg
                - **연비**: {row['연비']} km/l
                - **CO2 배출량**: {row['CO2배출량']} g/km
                """)

            st.markdown("---")

    st.success(f"총 {len(filtered)}개 트림이 조회되었습니다.")

def app():
    detail_ui()