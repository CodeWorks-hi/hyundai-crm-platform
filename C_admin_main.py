import streamlit as st
import pandas as pd
import uuid
import os
import importlib
from modules.C_admin_analytics import admin_analytics_ui
from modules.C_admin_inventory import admin_inventory_ui
from modules.C_admin_production import admin_production_ui
from modules.C_admin_eco import admin_eco_ui
from modules.C_admin_settings import admin_settings_ui

EMPLOYEE_CSV_PATH = "data/employee.csv"
EMPLOYEE_PHOTO_DIR = "data/employee_photos"

os.makedirs("data", exist_ok=True)
os.makedirs(EMPLOYEE_PHOTO_DIR, exist_ok=True)

def load_employees():
    if os.path.exists(EMPLOYEE_CSV_PATH):
        return pd.read_csv(EMPLOYEE_CSV_PATH)
    else:
        return pd.DataFrame(columns=["고유ID", "직원이름", "사진경로"])

def save_employees(df):
    df.to_csv(EMPLOYEE_CSV_PATH, index=False)

def app():
    st.title("본사 관리자 포털")

    tabs = st.tabs([
        "판매·수출 관리",
        "재고 및 공급망 관리",
        "생산·제조 현황",
        "탄소 배출량 모니터링",
        "설정 및 환경 관리"
    ])

    tab_modules = [
        ("modules.C_admin_analytics", "admin_analytics_ui"),       # 판매·수출 관리
        ("modules.C_admin_inventory", "admin_inventory_ui"),       # 재고 및 공급망 관리
        ("modules.C_admin_production", "admin_production_ui"),     # 생산·제조 현황
        ("modules.C_admin_eco", "admin_eco_ui"),                   # 탄소 배출량 모니터링
        ("modules.C_admin_settings", "admin_settings_ui"),         # 설정 및 환경 관리
    ]

    for i, (module_path, function_name) in enumerate(tab_modules):
        with tabs[i]:
            try:
                module = importlib.import_module(module_path)
                getattr(module, function_name)()
            except Exception as e:
                st.error(f"모듈 로딩 오류: {module_path}.{function_name} → {e}")

    st.markdown("---")
    if st.button("← 메인으로 돌아가기"):
        st.switch_page("Home.py")