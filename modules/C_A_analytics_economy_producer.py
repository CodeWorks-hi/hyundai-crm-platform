import time
from datetime import datetime, timedelta
from kafka import KafkaProducer
import requests
import json
import streamlit as st
import socket

# API 키 설정
EODHD_KEY = st.secrets["eodhd"]["API_token"]
FRED_KEY = st.secrets["fredaccount"]["API_Keys"]

# Kafka 서버 설정 (직접 IP 주소 사용)
KAFKA_SERVERS = [
    "192.168.0.100:9092",  # Kafka Broker 1
    "192.168.0.101:9092",  # Kafka Broker 2
    "192.168.0.102:9092"   # Kafka Broker 3
]

# DNS 캐시 클리어 (Unix/Linux 시스템 전용)
def clear_dns_cache():
    try:
        import os
        os.system("sudo systemd-resolve --flush-caches")
        print("DNS 캐시 초기화 완료")
    except:
        pass

clear_dns_cache()

# Kafka Producer 고급 설정
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    acks='all',
    retries=5,
    retry_backoff_ms=1000,
    api_version=(2,8,1),
    security_protocol='PLAINTEXT',
    socket_options=[
        (socket.SOL_SOCKET, socket.SO_REUSEADDR, 1),
        (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    ]
)

def get_economic_data():
    """4대 경제지표 수집 함수 (에러 처리 강화)"""
    now = datetime.utcnow()
    data = {
        'timestamp': now.timestamp(),
        'interest_rate': None,
        'usd_krw': None,
        'oil_price': None,
        'sp500': None,
        'data_delay': 0
    }

    try:
        # FRED 실시간 금리 데이터
        from fredapi import Fred
        fred = Fred(api_key=FRED_KEY)
        data['interest_rate'] = float(fred.get_series_latest_value('DFF'))
        data['data_delay'] = 0  # FRED는 실시간
    except Exception as e:
        print(f"FRED 데이터 수집 오류: {str(e)}")

    try:
        # EODHD 데이터 (15분 지연 반영)
        effective_time = now - timedelta(minutes=15)
        data['timestamp'] = effective_time.timestamp()
        
        usd_res = requests.get(
            f'https://eodhd.com/api/real-time/USD.KRW?api_token={EODHD_KEY}&fmt=json',
            timeout=10
        )
        if usd_res.status_code == 200:
            data['usd_krw'] = float(usd_res.json()['close'])
            data['data_delay'] = 15
            
        oil_res = requests.get(
            f'https://eodhd.com/api/real-time/CL.F?api_token={EODHD_KEY}&fmt=json',
            timeout=10
        )
        if oil_res.status_code == 200:
            data['oil_price'] = float(oil_res.json()['close'])
            
        sp500_res = requests.get(
            f'https://eodhd.com/api/real-time/SPY.US?api_token={EODHD_KEY}&fmt=json',
            timeout=10
        )
        if sp500_res.status_code == 200:
            data['sp500'] = float(sp500_res.json()['close'])
            
    except Exception as e:
        print(f"EODHD 데이터 수집 오류: {str(e)}")

    return data

if __name__ == "__main__":
    while True:
        start_time = time.time()
        
        data = get_economic_data()
        if data:
            try:
                future = producer.send('economic-indicators', data)
                metadata = future.get(timeout=10)
                print(f"전송 성공: {metadata.topic}-{metadata.partition}-{metadata.offset}")
            except Exception as e:
                print(f"카프카 전송 실패: {str(e)}")
                
        # 정확한 1분 간격 유지
        elapsed = time.time() - start_time
        sleep_time = max(60 - elapsed, 0)
        time.sleep(sleep_time)
