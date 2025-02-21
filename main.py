import streamlit as st
import requests
import pandas as pd
import json
from src import plot as pl

# Thiết lập layout cho trang hiển thị rộng hơn
st.set_page_config(layout="wide")

# URL của FastAPI (local hoặc URL trực tuyến)
API_URL = "http://localhost:8000"  # Thay đổi URL nếu cần

# Tiêu đề của ứng dụng
st.title("Stock Data & Financial Reports")

# Tạo navigation trên sidebar với các mục khác nhau
#navigation = st.sidebar.radio("Chọn mục", 
#                              ("Stock Data", 
#                               "Stock List",
#                               "Financial Business Report", 
#                               "Financial Report", 
#                               "Cashflow Report", 
#                               "Basic Index Report"))
navigation = st.sidebar.radio("Chọn mục", 
                              ("Stock Data", 
                               "Stock List",
                               "Crawl"))

# Nếu các tab khác (ngoại trừ Stock Data) thì nhập symbol có thể đặt ở sidebar,
# nhưng ở tab Stock Data, toàn bộ ô nhập sẽ được đặt trong phần chính.
#if navigation != "Stock Data":
#    symbol_sidebar = st.sidebar.text_input("Enter Stock Symbol (e.g., VND)", "VND")

# Các tab
if navigation == "Stock Data":
    st.header("Stock Data")
    with st.form(key="stock_data_form"):
        # Sắp xếp theo 2 cột
        col1, col2 = st.columns(2)
        with col1:
            symbol = st.text_input("Enter Stock Symbol (e.g., VND)", "VND")
            start_date = st.date_input("Start Date", pd.to_datetime("2021-02-01"))
        with col2:
            end_date = st.date_input("End Date", pd.to_datetime("2021-04-02"))
            data_source = st.text_input("Data Source", "CAFE")
        submit_stock = st.form_submit_button("Lấy Dữ liệu")
    
    if submit_stock:
        response = requests.get(
            f"{API_URL}/get_stock_data/{symbol}",
            params={"start_date": start_date, "end_date": end_date, "data_source": data_source}
        )
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            st.subheader(f"Stock Data for {symbol}")
            st.dataframe(df, use_container_width=True)
            
            st.subheader(f"{symbol} Candlestick Visualization")
            fig = pl.candle_stick(
                data=symbol,
                title=f"{symbol} symbol from {start_date} to {end_date}",
                xlab="Date",
                ylab="Price",
                start_date=str(start_date),
                end_date=str(end_date),
                data_source=str(data_source),
                show_advanced=["volume", "macd", "rsi"]
            )
            st.plotly_chart(fig)
        else:
            st.error(f"Error: {response.json().get('error', 'Unknown error')}")
            
elif navigation == "Stock List":
    st.header("Danh Mục Chứng Khoán")
    
    st.subheader("Chọn loại danh mục cần hiển thị")
    
    # Hàng 1: 2 checkbox
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        show_all = st.checkbox("All Symbols", value=True)
    with row1_col2:
        show_industries = st.checkbox("Symbols by Industries")
    
    # Hàng 2: 2 checkbox
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        show_exchange = st.checkbox("Symbols by Exchange")
    with row2_col2:
        show_icb = st.checkbox("Industries ICB")
    
    # Dưới các checkbox, đặt selectbox cho Symbols by Group
    group_option = st.selectbox("Symbols by Group", 
                                ["", "VN30", "VNMidCap", "VNSmallCap", "VNAllShare", "VN100", 
                                 "ETF", "HNX", "HNX30", "HNXCon", "HNXFin", "HNXLCap", 
                                 "HNXMSCap", "HNXMan", "UPCOM", "FU_INDEX", "CW"])
    
    if st.button("Lấy Danh mục"):
        stock_api = f"{API_URL}/stock-list"
        
        if show_all:
            r = requests.get(f"{stock_api}/all")
            if r.status_code == 200:
                df_all = pd.DataFrame(json.loads(r.text))
                st.subheader("All Symbols")
                st.dataframe(df_all, use_container_width=True)
            else:
                st.error("Lỗi khi lấy All Symbols")
                
        if show_industries:
            r = requests.get(f"{stock_api}/industries")
            if r.status_code == 200:
                df_ind = pd.DataFrame(json.loads(r.text))
                st.subheader("Symbols by Industries")
                st.dataframe(df_ind, use_container_width=True)
            else:
                st.error("Lỗi khi lấy Symbols by Industries")
                
        if show_exchange:
            r = requests.get(f"{stock_api}/exchange")
            print(r)
            if r.status_code == 200:
                df_ex = pd.DataFrame(json.loads(r.text))
                st.subheader("Symbols by Exchange")
                st.dataframe(df_ex, use_container_width=True)
            else:
                st.error("Lỗi khi lấy Symbols by Exchange")
                
        if show_icb:
            r = requests.get(f"{stock_api}/icb")
            if r.status_code == 200:
                df_icb = pd.DataFrame(json.loads(r.text))
                st.subheader("Industries ICB")
                st.dataframe(df_icb, use_container_width=True)
            else:
                st.error("Lỗi khi lấy Industries ICB")
                
        if group_option != "":
            r = requests.get(f"{stock_api}/group/{group_option}")
            if r.status_code == 200:
                df_group = pd.DataFrame([json.loads(r.text)]).T
                df_group.columns = ['Code']
                st.subheader(f"Symbols by Group: {group_option}")
                st.dataframe(df_group, use_container_width=True)
            else:
                st.error(f"Lỗi khi lấy Symbols by Group: {group_option}")

elif navigation == "Financial Business Report":
    with st.form(key="finance_business_form"):
        symbol_fb = st.text_input("Enter Stock Symbol (e.g., VND)", "VND")
        start_date_fb = st.date_input("Start Date", pd.to_datetime("2021-02-01"))
        end_date_fb = st.date_input("End Date", pd.to_datetime("2021-04-02"))
        data_source_fb = st.text_input("Data Source", "CAFE")
        submit_fb = st.form_submit_button("Get Data")
    if submit_fb:
        response = requests.get(
            f"{API_URL}/get_finance_business/{symbol_fb}",
            params={"start_date": start_date_fb, "end_date": end_date_fb}
        )
        if response.status_code == 200:
            data = response.json()["business_report"]
            df_business = pd.DataFrame(data)
            st.subheader(f"Financial Business Report for {symbol_fb}")
            st.dataframe(df_business, use_container_width=True)
        else:
            st.error(f"Error: {response.json().get('error', 'Unknown error')}")

elif navigation == "Financial Report":
    with st.form(key="finance_form"):
        symbol_f = st.text_input("Enter Stock Symbol (e.g., VND)", "VND")
        start_date_f = st.date_input("Start Date", pd.to_datetime("2021-02-01"))
        end_date_f = st.date_input("End Date", pd.to_datetime("2021-04-02"))
        data_source_f = st.text_input("Data Source", "CAFE")
        submit_f = st.form_submit_button("Get Data")
    if submit_f:
        response = requests.get(
            f"{API_URL}/get_finance_report/{symbol_f}",
            params={"start_date": start_date_f, "end_date": end_date_f}
        )
        if response.status_code == 200:
            data = response.json()["financial_report"]
            df_financial = pd.DataFrame(data)
            st.subheader(f"Financial Report for {symbol_f}")
            st.dataframe(df_financial, use_container_width=True)
        else:
            st.error(f"Error: {response.json().get('error', 'Unknown error')}")

elif navigation == "Cashflow Report":
    with st.form(key="cashflow_form"):
        symbol_cf = st.text_input("Enter Stock Symbol (e.g., VND)", "VND")
        start_date_cf = st.date_input("Start Date", pd.to_datetime("2021-02-01"))
        end_date_cf = st.date_input("End Date", pd.to_datetime("2021-04-02"))
        data_source_cf = st.text_input("Data Source", "CAFE")
        submit_cf = st.form_submit_button("Get Data")
    if submit_cf:
        response = requests.get(
            f"{API_URL}/get_cashflow_report/{symbol_cf}",
            params={"start_date": start_date_cf, "end_date": end_date_cf}
        )
        if response.status_code == 200:
            data = response.json()["cashflow_report"]
            df_cashflow = pd.DataFrame(data)
            st.subheader(f"Cashflow Report for {symbol_cf}")
            st.dataframe(df_cashflow, use_container_width=True)
        else:
            st.error(f"Error: {response.json().get('error', 'Unknown error')}")

elif navigation == "Basic Index Report":
    with st.form(key="basic_index_form"):
        symbol_bi = st.text_input("Enter Stock Symbol (e.g., VND)", "VND")
        start_date_bi = st.date_input("Start Date", pd.to_datetime("2021-02-01"))
        end_date_bi = st.date_input("End Date", pd.to_datetime("2021-04-02"))
        data_source_bi = st.text_input("Data Source", "CAFE")
        submit_bi = st.form_submit_button("Get Data")
    if submit_bi:
        response = requests.get(
            f"{API_URL}/get_basic_index/{symbol_bi}",
            params={"start_date": start_date_bi, "end_date": end_date_bi}
        )
        if response.status_code == 200:
            data = response.json()["basic_index"]
            df_basic_index = pd.DataFrame(data)
            st.subheader(f"Basic Index for {symbol_bi}")
            st.dataframe(df_basic_index, use_container_width=True)
        else:
            st.error(f"Error: {response.json().get('error', 'Unknown error')}")


elif navigation == "Crawl":
    st.header("Crawl Table Data")
    symbol_crawl = st.text_input("Enter Stock Symbol for Crawl", value="")
    
    if st.button("Crawl Now"):
        if not symbol_crawl.strip():
            st.warning("Vui lòng nhập mã chứng khoán trước khi crawl.")
        else:
            with st.spinner("Đang crawl dữ liệu..."):
                response = requests.get(f"{API_URL}/crawl_table", params={"symbol": symbol_crawl.strip()})
            if response.status_code == 200:
                resp_json = response.json()
                if "message" in resp_json:
                    st.info(resp_json["message"])
                else:
                    total_pages = resp_json.get("total_pages", 0)
                    data = resp_json.get("data", [])
                    
                    st.subheader(f"Tổng số trang (theo phân trang): {total_pages}")
                    
                    # Hiển thị thanh tiến trình giả lập dựa trên số trang
                    progress_bar = st.progress(0)
                    for i in range(total_pages):
                        progress_bar.progress((i + 1) / total_pages)
                        # Nếu muốn thấy hiệu ứng progress, có thể thêm delay (không bắt buộc)
                        # time.sleep(0.05)
                    
                    df = pd.DataFrame(data)
                    st.subheader("Crawled Data")
                    st.dataframe(df, use_container_width=True)
            else:
                st.error(f"Error: {response.json().get('error', 'Unknown error')}")