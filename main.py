import streamlit as st
import requests
import pandas as pd
import json
from src.plot import plot as pl
from src.plot import plot_foreign as plf
from src.plot import plot_crawl as plc
from datetime import datetime

# Thiết lập layout cho trang hiển thị rộng hơn
st.set_page_config(layout="wide")

# URL của FastAPI (local hoặc URL trực tuyến)
API_URL = "http://localhost:8000"  # Thay đổi URL nếu cần

# Tiêu đề của ứng dụng
st.title("STOCK DATA AOF RESEARCH 2025")

# Tạo navigation trên sidebar với các mục khác nhau, đã thêm mục "Giá trị khớp lệnh"
navigation = st.sidebar.radio("Chọn mục", 
                              ("Dữ liệu chứng khoán Việt Nam", 
                               "Danh mục chứng khoán Việt Nam",
                               "Thông tin mã chứng khoán Việt Nam",
                               "Giá trị khớp lệnh",
                               "Crawl",
                               "Chứng khoán nước ngoài"))

# Các tab
if navigation == "Dữ liệu chứng khoán Việt Nam":
    st.header("Dữ liệu chứng khoán Việt Nam")
    with st.form(key="stock_data_form"):
        # Sắp xếp theo 2 cột
        col1, col2 = st.columns(2)
        with col1:
            symbol = st.text_input("Nhập mã chứng khoán: (e.g., VND)", "VND")
        with col2:
            start_date = st.date_input("Ngày đầu", pd.to_datetime("2020-01-01"))
            end_date = st.date_input("Ngày cuối", pd.to_datetime("2021-01-01"))
            #data_source = st.text_input("Data Source", "CAFE")
        submit_stock = st.form_submit_button("Lấy Dữ liệu")
    
    if submit_stock:
        response = requests.get(
            f"{API_URL}/get_stock_data/{symbol}",
            params={"start_date": start_date, "end_date": end_date}
        )
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            st.subheader(f"Dữ liệu chứng khoán Việt Nam của {symbol}")
            st.dataframe(df, use_container_width=True)
            
            st.subheader(f"{symbol} Candlestick Visualization")
            fig = pl.candle_stick(
                data=symbol,
                title=f"{symbol} symbol from {start_date} to {end_date}",
                xlab="Date",
                ylab="Price",
                start_date=str(start_date),
                end_date=str(end_date),
                data_source='CAFEF',
                show_advanced=["volume", "macd", "rsi"]
            )
            st.plotly_chart(fig)
        else:
            st.error(f"Error: {response.json().get('error', 'Unknown error')}")
            
elif navigation == "Danh mục chứng khoán Việt Nam":
    st.header("Danh Mục Chứng Khoán")
    
    st.subheader("Chọn loại danh mục cần hiển thị")
    
    # Hàng 1: 2 checkbox
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        show_all = st.checkbox("Tất cả", value=True)
    with row1_col2:
        show_industries = st.checkbox("Mã theo ngành")
    
    # Hàng 2: 2 checkbox
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        show_exchange = st.checkbox("Mã theo sàn giao dịch")
    with row2_col2:
        show_icb = st.checkbox("Industry Classification Benchmark (ICB)")
    
    # Dưới các checkbox, đặt selectbox cho Symbols by Group
    group_option = st.selectbox("Mã theo nhóm", 
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

elif navigation == "Giá trị khớp lệnh":
    st.header(f"Giá trị khớp lệnh trong phiên gần nhất với ngày hiện tại: {datetime.now().date()}")
    with st.form(key="intraday_form"):
        symbol_intraday = st.text_input("Nhập mã chứng khoán", "ACB")
        page_size = st.number_input("Page Size", min_value=1, value=100, step=1)
        submit_intraday = st.form_submit_button("Lấy dữ liệu khớp lệnh")
    
    if submit_intraday:
        params = {"page_size": page_size}
        response = requests.get(f"{API_URL}/get_intraday_data/{symbol_intraday}", params=params)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                df = pd.DataFrame([data])
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                raise ValueError("Dữ liệu trả về không đúng định dạng mong đợi")
            st.subheader(f"Dữ liệu khớp lệnh của {symbol_intraday}")
            st.dataframe(df, use_container_width=True)
        else:
            st.error(f"Error: {response.json().get('error', 'Unknown error')}")
            
elif navigation == "Crawl":
    st.header("Crawl Dữ liệu chứng khoán")
    symbol_crawl = st.text_input("Nhập mã chứng khoán để Crawl", value="")
    
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
                    
                    progress_bar = st.progress(0)
                    for i in range(total_pages):
                        progress_bar.progress((i + 1) / total_pages)
                    
                    df = pd.DataFrame(data)
                    #print(df.describe())
                    #print(df.info())
                    st.subheader("Dữ liệu đã truy xuất")
                    st.dataframe(df, use_container_width=True)
                    fig = plc.candle_stick_df(df, title=f"{symbol_crawl} Ticker History")
                    st.plotly_chart(fig)
            else:
                st.error(f"Error: {response.json().get('error', 'Unknown error')}")

elif navigation == "Thông tin mã chứng khoán Việt Nam":
    st.header("Thông tin mã chứng khoán Việt Nam")
    # Nhập mã chứng khoán cần lấy thông tin
    symbol = st.text_input("Nhập Mã chứng khoán", "VCB")
    
    st.subheader("Chọn thông tin cần lấy:")
    # Các option có sẵn
    options = ["Overview", "Profile", "Shareholders", "Insider Deals", 
               "Subsidiaries", "Officers", "Events", "News", "Dividends"]
    
    # Sắp xếp các option vào 3 cột theo thứ tự:
    # Cột 1: Overview, Insider Deals, Events
    # Cột 2: Profile, Subsidiaries, News
    # Cột 3: Shareholders, Officers, Dividends
    col1, col2, col3 = st.columns(3)
    selected_options = []
    if col1.checkbox("Overview", key="overview"): 
        selected_options.append("Overview")
    if col1.checkbox("Insider Deals", key="insider_deals"): 
        selected_options.append("Insider Deals")
    if col1.checkbox("Events", key="events"): 
        selected_options.append("Events")
    
    if col2.checkbox("Profile", key="profile"): 
        selected_options.append("Profile")
    if col2.checkbox("Subsidiaries", key="subsidiaries"): 
        selected_options.append("Subsidiaries")
    if col2.checkbox("News", key="news"): 
        selected_options.append("News")
    
    if col3.checkbox("Shareholders", key="shareholders"): 
        selected_options.append("Shareholders")
    if col3.checkbox("Officers", key="officers"): 
        selected_options.append("Officers")
    if col3.checkbox("Dividends", key="dividends"): 
        selected_options.append("Dividends")
    
    # Các endpoint hỗ trợ phân trang
    pagination_options = ["Insider Deals", "Subsidiaries", "Officers", "Events", "News", "Dividends"]
    # Tạo dict chứa các tham số phân trang cho từng API hỗ trợ
    pagination_params = {}
    for opt in selected_options:
        if opt in pagination_options:
            with st.expander(f"Thiết lập phân trang cho {opt}"):
                page_size_val = st.number_input(f"Page Size cho {opt}", min_value=1, value=20, key=f"page_size_{opt}")
                page_val = st.number_input(f"Page (số thứ tự trang) cho {opt}", min_value=0, value=0, key=f"page_{opt}")
                pagination_params[opt] = {"page_size": page_size_val, "page": page_val}
    
    if st.button("Lấy thông tin"):
        for opt in selected_options:
            # Xác định endpoint dựa trên option đã chọn
            if opt == "Overview":
                endpoint = f"/overview/{symbol}"
                params = {}
            elif opt == "Profile":
                endpoint = f"/profile/{symbol}"
                params = {}
            elif opt == "Shareholders":
                endpoint = f"/shareholders/{symbol}"
                params = {}
            elif opt == "Insider Deals":
                endpoint = f"/insider_deals/{symbol}"
                params = pagination_params.get("Insider Deals", {})
            elif opt == "Subsidiaries":
                endpoint = f"/subsidiaries/{symbol}"
                params = pagination_params.get("Subsidiaries", {})
            elif opt == "Officers":
                endpoint = f"/officers/{symbol}"
                params = pagination_params.get("Officers", {})
            elif opt == "Events":
                endpoint = f"/events/{symbol}"
                params = pagination_params.get("Events", {})
            elif opt == "News":
                endpoint = f"/news/{symbol}"
                params = pagination_params.get("News", {})
            elif opt == "Dividends":
                endpoint = f"/dividends/{symbol}"
                params = pagination_params.get("Dividends", {})
            
            url = f"{API_URL}{endpoint}"
            # Gọi API với hoặc không có params phân trang
            response = requests.get(url, params=params) if params else requests.get(url)
            if response.status_code == 200:
                data = response.json()
                st.subheader(f"Kết quả - {opt} của {symbol}")
                # Hiển thị dữ liệu dạng bảng nếu có thể
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                elif isinstance(data, dict):
                    try:
                        df = pd.DataFrame([data])
                        st.dataframe(df, use_container_width=True)
                    except Exception as e:
                        st.error("Không thể chuyển đổi dữ liệu thành bảng.")
                else:
                    st.error("Dữ liệu trả về không đúng định dạng bảng.")
            else:
                st.error(f"Error: {response.json().get('error', 'Unknown error')}")

elif navigation == "Chứng khoán nước ngoài":
    st.header("Dữ liệu chứng khoán thế giới")
    # Nhập mã chứng khoán nước ngoài
    symbol_foreign = st.text_input("Nhập mã cổ phiếu nước ngoài:", "MSFT")
    
    st.write("Chọn chức năng cần truy xuất:")
    col1, col2 = st.columns(2)
    with col1:
        ticker_info_selected = st.checkbox("Ticker Info", key="foreign_ticker_info")
        ticker_calendar_selected = st.checkbox("Ticker Calendar", key="foreign_ticker_calendar")
    with col2:
        ticker_analyst_selected = st.checkbox("Ticker Analyst Price Targets", key="foreign_ticker_analyst")
        ticker_history_selected = st.checkbox("Ticker History", key="foreign_ticker_history")
        # Nếu chọn Ticker History thì hiển thị selectbox chọn khoảng thời gian
        if ticker_history_selected:
            period = st.selectbox(
                "Chọn khoảng thời gian", 
                options=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
                key="foreign_ticker_history_period"
            )
    
    if st.button("Lấy dữ liệu"):
        # Xử lý Ticker Info
        if ticker_info_selected:
            url = f"{API_URL}/ticker/info/{symbol_foreign}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                st.subheader(f"Kết quả - Ticker Info của {symbol_foreign}")
                if isinstance(data, dict):
                    df = pd.DataFrame([data])
                    st.dataframe(df, use_container_width=True)
                elif isinstance(data, list):
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.json(data)
            else:
                st.error(f"Error: {response.json().get('error', 'Unknown error')}")
        
        # Xử lý Ticker Calendar
        if ticker_calendar_selected:
            url = f"{API_URL}/ticker/calendar/{symbol_foreign}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                st.subheader(f"Kết quả - Ticker Calendar của {symbol_foreign}")
                if isinstance(data, dict):
                    df = pd.DataFrame([data])
                    st.dataframe(df, use_container_width=True)
                elif isinstance(data, list):
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.json(data)
            else:
                st.error(f"Error: {response.json().get('error', 'Unknown error')}")
        
        # Xử lý Ticker Analyst Price Targets
        if ticker_analyst_selected:
            url = f"{API_URL}/ticker/analyst-price-targets/{symbol_foreign}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                st.subheader(f"Kết quả - Ticker Analyst Price Targets của {symbol_foreign}")
                if isinstance(data, dict):
                    df = pd.DataFrame([data])
                    st.dataframe(df, use_container_width=True)
                elif isinstance(data, list):
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.json(data)
            else:
                st.error(f"Error: {response.json().get('error', 'Unknown error')}")
        
        # Xử lý Ticker History với tham số period
        if ticker_history_selected:
            url = f"{API_URL}/ticker/history/{symbol_foreign}"
            response = requests.get(url, params={"period": period})
            if response.status_code == 200:
                data = response.json()
                st.subheader(f"Kết quả - Ticker History của {symbol_foreign} với period {period}")
                if isinstance(data, dict):
                    df = pd.DataFrame([data])
                    st.dataframe(df, use_container_width=True)
                elif isinstance(data, list):
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    fig = plf.candle_stick_df(df, title=f"{symbol_foreign} Ticker History ({period})")
                    st.plotly_chart(fig)
                else:
                    st.json(data)
            else:
                st.error(f"Error: {response.json().get('error', 'Unknown error')}")
