# 판매·수출 관리
    # 판매·수출 관리 
        # 해외 판매(수출 관리)수출입 국가별 분석
            # 해외  시장 비교



import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import urllib3
import re

def export_region_ui():
    st.subheader("판매·수출 관리")
    st.write("해외 판매 실적을 분석하는 페이지입니다.")
    st.write("수출입 국가별 실적 분석")
    st.write("해외 시장 비교")


