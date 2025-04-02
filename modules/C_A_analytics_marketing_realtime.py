import streamlit as st
from kafka import KafkaConsumer
import pandas as pd
import json
from datetime import datetime
import plotly.express as px
from pathlib import Path

# 환경 설정
HISTORY_FILE = Path("economic_history.csv")
BUFFER_SIZE = 96  # 15분 간격 24시간 데이터

# 히스토리 데이터 관리
@st.cache_data
def load_history():
    try:
        df = pd.read_csv(HISTORY_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        return df.sort_values('timestamp')
    except:
        return pd.DataFrame(columns=['timestamp', 'usd_krw', 'oil_price', 'sp500', 'interest_rate'])

def save_history(df):
    df.to_csv(HISTORY_FILE, index=False)

# 실시간 시각화 패널 생성 함수
def create_metric_panel(col, title, value, delta, delay, history, current_data, key, is_currency=True):
    with col:
        st.markdown(f"### {title}")
        
        # 메트릭 표시
        value_str = f"{value:,.1f}원" if is_currency else f"{value:,.2f}"
        delta_str = f"{delta:+,.1f}" if is_currency else f"{delta:+,.2f}"
        st.metric(
            label="현재 값",
            value=value_str,
            delta=delta_str,
            help=f"데이터 지연: {delay}분" if delay > 0 else "실시간 데이터"
        )
        
        # 통합 차트 생성
        df_combined = pd.concat([
            history[['timestamp', key]].rename(columns={'timestamp': '시간'}),
            pd.DataFrame({
                '시간': [datetime.fromtimestamp(ts) for ts in current_data['timestamp']],
                key: current_data[key]
            })
        ])
        
        fig = px.line(
            df_combined,
            x='시간',
            y=key,
            title=f"{title} 24시간 추이",
            labels={'value': '값', '시간': ''},
            height=300
        )
        fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

# 메인 대시보드
def marketing_realtime_ui():
    st.title("실시간 경제지표 모니터링 센터")
    
    # 초기 데이터 로드
    history_df = load_history()
    realtime_data = {
        'timestamp': [], 'usd_krw': [], 'oil_price': [],
        'sp500': [], 'interest_rate': []
    }
    
    # Kafka 컨슈머 설정
    consumer = KafkaConsumer(
        'economic-indicators',
        bootstrap_servers=st.secrets["kafka"]["bootstrap_servers"].split(","),
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='latest',
        consumer_timeout_ms=1000
    )
    
    placeholder = st.empty()
    
    for msg in consumer:
        data = msg.value
        
        # 데이터 버퍼 업데이트
        for key in realtime_data:
            if key in data:
                realtime_data[key].append(data[key])
                if len(realtime_data[key]) > BUFFER_SIZE:
                    realtime_data[key].pop(0)
        
        # 히스토리 저장
        if datetime.fromtimestamp(data['timestamp']).minute % 15 == 0:
            new_row = pd.DataFrame({k: [v[-1]] for k,v in realtime_data.items() if k != 'data_delay'})
            updated_df = pd.concat([history_df, new_row]).drop_duplicates()
            save_history(updated_df)
        
        # 실시간 렌더링
        with placeholder.container():
            cols = st.columns(4)
            current_time = datetime.now()
            
            # 1. 환율 패널
            create_metric_panel(
                cols[0],
                "💵 USD/KRW 환율",
                realtime_data['usd_krw'][-1] if realtime_data['usd_krw'] else 0,
                realtime_data['usd_krw'][-1] - realtime_data['usd_krw'][-2] if len(realtime_data['usd_krw'])>1 else 0,
                data.get('data_delay', 0),
                history_df,
                realtime_data,
                'usd_krw'
            )
            
            # 2. 금리 패널
            create_metric_panel(
                cols[1],
                "🏦 미국 기준금리",
                realtime_data['interest_rate'][-1] if realtime_data['interest_rate'] else 0,
                realtime_data['interest_rate'][-1] - realtime_data['interest_rate'][-2] if len(realtime_data['interest_rate'])>1 else 0,
                0,  # FRED는 실시간
                history_df,
                realtime_data,
                'interest_rate',
                is_currency=False
            )
            
            # 3. 유가 패널
            create_metric_panel(
                cols[2],
                "🛢️ WTI 유가",
                realtime_data['oil_price'][-1] if realtime_data['oil_price'] else 0,
                realtime_data['oil_price'][-1] - realtime_data['oil_price'][-2] if len(realtime_data['oil_price'])>1 else 0,
                data.get('data_delay', 0),
                history_df,
                realtime_data,
                'oil_price',
                is_currency=False
            )
            
            # 4. S&P500 패널
            create_metric_panel(
                cols[3],
                "📈 S&P 500",
                realtime_data['sp500'][-1] if realtime_data['sp500'] else 0,
                realtime_data['sp500'][-1] - realtime_data['sp500'][-2] if len(realtime_data['sp500'])>1 else 0,
                data.get('data_delay', 0),
                history_df,
                realtime_data,
                'sp500',
                is_currency=False
            )


