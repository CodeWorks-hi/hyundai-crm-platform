import streamlit as st
import pandas as pd
import importlib
from modules.A_U_carousel import render_carousel
import base64

 # 차량 이미지 캐러셀 (Swiper.js 활용)
car_data = [
    {"name": "IONIQ 9", "url": "https://www.hyundai.com/contents/mainbanner/main_kv_ioniq9-pc.png"},
    {"name": "Palisade", "url": "https://www.hyundai.com/contents/mainbanner/Main-KV_Car_PALISADE.png"},
    {"name": "Venue", "url": "https://www.hyundai.com/contents/mainbanner/Main-KV_Car_venue.png"},
    {"name": "Tucson", "url": "https://www.hyundai.com/contents/mainbanner/Main-KV_Car_TUCSON.png"},
    {"name": "Sonata", "url": "https://www.hyundai.com/contents/mainbanner/main_sonata_25my_w.png"},
    {"name": "Santa Fe", "url": "https://www.hyundai.com/contents/mainbanner/main-santafe-25my-kv-w.png"},
    {"name": "Casper Electric", "url": "https://www.hyundai.com/contents/mainbanner/Main-KV_Car_CASPER-Electric.png"},
]

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()
def home_ui():
    # 캐러셀 함수 ( 파라미터에 차 리스트 넣으면 실행 됨) 모듈 > A_U_carousel.py 만 수정
    render_carousel(car_data, height=400)