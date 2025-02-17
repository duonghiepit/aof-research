import streamlit as st
import requests
import pandas as pd
from src import plot as pl

# URL của FastAPI (local hoặc URL trực tuyến)
API_URL = "http://localhost:8000"  # Thay đổi URL nếu bạn triển khai lên server khác

# Tiêu đề của ứng dụng
st.title("Stock Data & Financial Reports")

# Thêm phần lựa chọn mã chứng khoán và thời gian
symbol = st.text_input("Enter Stock Symbol (e.g., VND)", "VND")
start_date = st.date_input("Start Date", pd.to_datetime("2021-02-01"))
end_date = st.date_input("End Date", pd.to_datetime("2021-04-02"))

# Nút để lấy dữ liệu chứng khoán
if st.button("Get Stock Data"):
    # Gửi yêu cầu tới FastAPI để lấy dữ liệu chứng khoán
    response = requests.get(f"{API_URL}/get_stock_data/{symbol}",
                            params={"start_date": start_date, "end_date": end_date})
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        # Hiển thị dữ liệu
        st.subheader(f"Stock Data for {symbol}")
        st.write(df)

        # Sử dụng hàm vnquant_candle_stick để trực quan hóa dữ liệu chứng khoán
        st.subheader(f"{symbol} Candlestick Visualization")
        pl.vnquant_candle_stick(
            data=symbol,
            title=f"{symbol} symbol from {start_date} to {end_date}",
            xlab="Date",
            ylab="Price",
            start_date=str(start_date),
            end_date=str(end_date),
            data_source="CAFE",  # Hoặc "VND" tùy thuộc vào nguồn dữ liệu bạn sử dụng
            show_advanced=["volume", "macd", "rsi"]
        )
    else:
        st.error(f"Error: {response.json().get('error', 'Unknown error')}")

# Thêm phần yêu cầu báo cáo tài chính
if st.button("Get Financial Reports"):
    # Gửi yêu cầu tới FastAPI để lấy báo cáo tài chính
    response = requests.get(f"{API_URL}/get_finance_business/{symbol}",
                            params={"start_date": start_date, "end_date": end_date})
    if response.status_code == 200:
        data = response.json()["business_report"]
        df_business = pd.DataFrame(data)

        # Hiển thị báo cáo tài chính doanh nghiệp
        st.subheader(f"Financial Business Report for {symbol}")
        st.write(df_business)
    else:
        st.error(f"Error: {response.json().get('error', 'Unknown error')}")

# Thêm phần báo cáo tài chính (Financial Report)
if st.button("Get Financial Report"):
    response = requests.get(f"{API_URL}/get_finance_report/{symbol}",
                            params={"start_date": start_date, "end_date": end_date})
    if response.status_code == 200:
        data = response.json()["financial_report"]
        df_financial = pd.DataFrame(data)

        # Hiển thị báo cáo tài chính
        st.subheader(f"Financial Report for {symbol}")
        st.write(df_financial)
    else:
        st.error(f"Error: {response.json().get('error', 'Unknown error')}")

# Thêm phần báo cáo dòng tiền (Cash Flow Report)
if st.button("Get Cashflow Report"):
    response = requests.get(f"{API_URL}/get_cashflow_report/{symbol}",
                            params={"start_date": start_date, "end_date": end_date})
    if response.status_code == 200:
        data = response.json()["cashflow_report"]
        df_cashflow = pd.DataFrame(data)

        # Hiển thị báo cáo dòng tiền
        st.subheader(f"Cashflow Report for {symbol}")
        st.write(df_cashflow)
    else:
        st.error(f"Error: {response.json().get('error', 'Unknown error')}")

# Thêm phần báo cáo chỉ số cơ bản (Basic Index Report)
if st.button("Get Basic Index Report"):
    response = requests.get(f"{API_URL}/get_basic_index/{symbol}",
                            params={"start_date": start_date, "end_date": end_date})
    if response.status_code == 200:
        data = response.json()["basic_index"]
        df_basic_index = pd.DataFrame(data)

        # Hiển thị báo cáo chỉ số cơ bản
        st.subheader(f"Basic Index for {symbol}")
        st.write(df_basic_index)
    else:
        st.error(f"Error: {response.json().get('error', 'Unknown error')}")
