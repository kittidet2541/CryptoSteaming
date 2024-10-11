import requests
import time
import pandas as pd
import streamlit as st
from datetime import datetime
import altair as alt

# รายชื่อเหรียญที่ต้องการดึงข้อมูล
symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT",
           "XRPUSDT", "DOTUSDT", "DOGEUSDT", "LINKUSDT", "LTCUSDT"]

# ฟังก์ชันเพื่อดึงข้อมูลจาก Binance API
def fetch_binance_data():
    url = "https://api.binance.com/api/v3/ticker/price"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        prices = {item['symbol']: item['price'] for item in data if item['symbol'] in symbols}
        return prices
    else:
        print(f"Error fetching data: {response.status_code}")
        return {}

# ตั้งค่าหน้า Streamlit
st.title("Binance Cryptocurrency Prices")
st.write("ข้อมูลราคาของเหรียญที่ดึงจาก Binance API")

# ตรวจสอบว่า session_state มีข้อมูลหรือไม่ ถ้าไม่มีให้สร้าง
if 'historical_data' not in st.session_state:
    st.session_state.historical_data = []

# สร้างพื้นที่สำหรับ DataFrame และกราฟ
df_placeholder = st.empty()
chart_placeholder = st.empty()

# วนลูปเพื่อตรวจสอบข้อมูลทุก 5 วินาที
while True:
    binance_data = fetch_binance_data()
    if binance_data:  # ตรวจสอบว่ามีข้อมูลหรือไม่
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_with_timestamp = [{'timestamp': timestamp, 'coin': coin, 'value': float(value)} 
                                for coin, value in binance_data.items()]

        # เพิ่มข้อมูลใหม่ลงใน session_state
        st.session_state.historical_data.extend(data_with_timestamp)

        # แสดง DataFrame เฉพาะราคาล่าสุด
        latest_data = pd.DataFrame(data_with_timestamp)
        df_placeholder.dataframe(latest_data)

        # สร้างกราฟหุ้นด้วย Altair
        historical_df = pd.DataFrame(st.session_state.historical_data)
        chart = alt.Chart(historical_df).mark_line().encode(
            x='timestamp:T',
            y='value:Q',
            color='coin:N'
        ).properties(
            width=800,
            height=400
        )

        # แสดงกราฟในพื้นที่ที่สร้างขึ้น
        chart_placeholder.altair_chart(chart, use_container_width=True)

    time.sleep(5)  # รอ 5 วินาทีก่อนดึงข้อมูลใหม่
