from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from src.data import DataLoader
from src.explore.vci.listing import Listing
from src.explore.vci.quote import Quote
from src.crawl.scraper import crawl_table_data
from src.explore.tcbs.company import Company
from typing import Optional
import pandas as pd
import numpy as np
import yfinance as yf
import datetime
import math
import json

# Khởi tạo FastAPI
app = FastAPI()

listing = Listing(random_agent=True, show_log=False)

# API để lấy dữ liệu chứng khoán
@app.get("/get_stock_data/{symbol}")
async def get_stock_data(symbol: str, start_date: str, end_date: str, data_source: str = "CAFE"):
    try:
        # Khởi tạo DataLoader và tải dữ liệu
        loader = DataLoader(symbol, start_date, end_date, data_source=data_source, minimal=True)
        data = loader.download()

        # Kiểm tra nếu data là một DataFrame
        if isinstance(data, pd.DataFrame):
            # Reset index để loại bỏ nếu có index không hợp lệ (ví dụ: tuple)
            data = data.reset_index()
            # Chuyển DataFrame thành danh sách các bản ghi (records)
            # Đảm bảo rằng các cột như 'Symbols', 'date' không phải là tuple hoặc có tên hợp lệ
            data_json = data.to_dict(orient="records")
            cleaned_data_json = [{key[0]: value for key, value in record.items()} for record in data_json]
            print(cleaned_data_json[:1])
        else:
            # Nếu data không phải DataFrame, trả về lỗi
            raise ValueError("Data is not a DataFrame")

        # Trả về kết quả dưới dạng JSON
        #return JSONResponse(content={"data": cleaned_data_json})
        return cleaned_data_json

    except Exception as e:
        # Trả về lỗi nếu có
        return JSONResponse(content={"error": str(e)}, status_code=400)

@app.get("/stock-list/all", tags=["Stock List"])
def get_all_symbols():
    try:
        # Trả về JSON dạng record
        return listing.all_symbols(show_log=False, to_df=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock-list/industries", tags=["Stock List"])
def get_symbols_by_industries():
    try:
        return listing.symbols_by_industries(show_log=False, to_df=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock-list/exchange", tags=["Stock List"])
def get_symbols_by_exchange():
    try:
        df = listing.symbols_by_exchange(show_log=False, to_df=True)
        result = json.loads(df.to_json(orient="records"))
        return result
        #return listing.symbols_by_exchange(show_log=False, to_df=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock-list/icb", tags=["Stock List"])
def get_industries_icb():
    try:
        df = listing.industries_icb(show_log=False, to_df=True)
        result = json.loads(df.to_json(orient="records"))
        return result
        #return listing.industries_icb(show_log=False, to_df=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock-list/group/{group}", tags=["Stock List"])
def get_symbols_by_group(group: str):
    try:
        return listing.symbols_by_group(group=group, show_log=False, to_df=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/crawl_table", tags=["Crawl"])
def crawl_table(symbol: str = None):
    if not symbol:
        return JSONResponse(content={"message": "Vui lòng cung cấp mã chứng khoán."}, status_code=200)
    try:
        df, total_pages = crawl_table_data(symbol)
        data_json = df.to_dict(orient="records")
        return JSONResponse(content={"data": data_json, "total_pages": total_pages})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_intraday_data/{symbol}")
async def get_intraday_data(
    symbol: str,
    page_size: int = 100,
    last_time: Optional[str] = None,
    to_df: bool = True,
    show_log: bool = False
):
    try:
        # Khởi tạo đối tượng Quote với mã chứng khoán
        quote = Quote(symbol, show_log=show_log)
        # Gọi hàm intraday để lấy dữ liệu khớp lệnh
        data = quote.intraday(
            page_size=page_size,
            last_time=last_time,
            to_df=to_df,
            show_log=show_log
        )
        
        # Nếu dữ liệu trả về là DataFrame, chuyển sang danh sách các dictionary (records)
        if isinstance(data, pd.DataFrame):
            data = data.reset_index(drop=True)
            data_json = data.to_dict(orient="records")
        else:
            data_json = data
        
        return data_json

    except Exception as e:
        return {"error": str(e)}


def convert_numpy_types(data):
    if isinstance(data, dict):
        return {k: convert_numpy_types(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_types(item) for item in data]
    elif isinstance(data, np.integer):
        return int(data)
    elif isinstance(data, np.floating):
        if np.isnan(data) or np.isinf(data):
            return None
        return float(data)
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            return None
        return data
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, pd.Timestamp):
        return data.isoformat()
    # Xử lý đối tượng datetime.date
    elif isinstance(data, datetime.date):
        return data.isoformat()
    else:
        return data

@app.get("/overview/{symbol}", tags=["Stock Information"])
async def company_overview(symbol: str):
    try:
        comp = Company(symbol, to_df=True)
        result = comp.overview()
        # Nếu trả về DataFrame thì chuyển sang dictionary dạng list
        if isinstance(result, pd.DataFrame):
            result = result.to_dict(orient="records")
        result = convert_numpy_types(result)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profile/{symbol}", tags=["Stock Information"])
async def company_profile(symbol: str):
    try:
        comp = Company(symbol, to_df=True)
        result = comp.profile()
        if isinstance(result, pd.DataFrame):
            result = result.to_dict(orient="records")
        result = convert_numpy_types(result)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/shareholders/{symbol}", tags=["Stock Information"])
async def company_shareholders(symbol: str):
    try:
        comp = Company(symbol, to_df=True)
        result = comp.shareholders()
        if isinstance(result, pd.DataFrame):
            result = result.to_dict(orient="records")
        result = convert_numpy_types(result)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/insider_deals/{symbol}", tags=["Stock Information"])
async def company_insider_deals(symbol: str, page_size: int = 20, page: int = 0):
    try:
        comp = Company(symbol, to_df=True)
        result = comp.insider_deals(page_size=page_size, page=page)
        if isinstance(result, pd.DataFrame):
            result = result.to_dict(orient="records")
        result = convert_numpy_types(result)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/subsidiaries/{symbol}", tags=["Stock Information"])
async def company_subsidiaries(symbol: str, page_size: int = 100, page: int = 0):
    try:
        comp = Company(symbol, to_df=True)
        result = comp.subsidiaries(page_size=page_size, page=page)
        if isinstance(result, pd.DataFrame):
            result = result.to_dict(orient="records")
        result = convert_numpy_types(result)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/officers/{symbol}", tags=["Stock Information"])
async def company_officers(symbol: str, page_size: int = 20, page: int = 0):
    try:
        comp = Company(symbol, to_df=True)
        result = comp.officers(page_size=page_size, page=page)
        if isinstance(result, pd.DataFrame):
            result = result.to_dict(orient="records")
        result = convert_numpy_types(result)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/{symbol}", tags=["Stock Information"])
async def company_events(symbol: str, page_size: int = 15, page: int = 0):
    try:
        comp = Company(symbol, to_df=True)
        result = comp.events(page_size=page_size, page=page)
        if isinstance(result, pd.DataFrame):
            result = result.to_dict(orient="records")
        result = convert_numpy_types(result)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news/{symbol}", tags=["Stock Information"])
async def company_news(symbol: str, page_size: int = 15, page: int = 0):
    try:
        comp = Company(symbol, to_df=True)
        result = comp.news(page_size=page_size, page=page)
        if isinstance(result, pd.DataFrame):
            result = result.to_dict(orient="records")
        result = convert_numpy_types(result)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dividends/{symbol}", tags=["Stock Information"])
async def company_dividends(symbol: str, page_size: int = 15, page: int = 0):
    try:
        comp = Company(symbol, to_df=True)
        result = comp.dividends(page_size=page_size, page=page)
        if isinstance(result, pd.DataFrame):
            result = result.to_dict(orient="records")
        result = convert_numpy_types(result)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------- Tích hợp API yfinance ----------------------

@app.get("/ticker/info/{symbol}", tags=["Foreign"])
def ticker_info(symbol: str):
    """
    Lấy thông tin tổng quan của công ty.
    Chức năng: Trả về một dictionary chứa thông tin chung về công ty như mô tả, ngành nghề, số liệu tài chính, v.v.
    """
    try:
        dat = yf.Ticker(symbol)
        info = dat.info
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/calendar/{symbol}", tags=["Foreign"])
def ticker_calendar(symbol: str):
    """
    Lấy lịch sự kiện của công ty.
    Chức năng: Trả về thông tin lịch (ví dụ: ngày công bố báo cáo tài chính, các sự kiện quan trọng) của công ty.
    """
    try:
        dat = yf.Ticker(symbol)
        calendar = dat.calendar
        # Nếu calendar có thuộc tính to_dict (ví dụ: DataFrame), chuyển đổi sang dict; nếu không thì giữ nguyên
        if hasattr(calendar, "to_dict"):
            calendar = calendar.to_dict()
        # Chuyển đổi các giá trị không JSON-compliant (như datetime.date) thành chuỗi ISO
        calendar = convert_numpy_types(calendar)
        return calendar
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/analyst-price-targets/{symbol}", tags=["Foreign"])
def ticker_analyst_price_targets(symbol: str):
    """
    Lấy mục tiêu giá cổ phiếu từ các nhà phân tích.
    Chức năng: Trả về thông tin dự báo giá cổ phiếu do các nhà phân tích đưa ra.
    """
    try:
        dat = yf.Ticker(symbol)
        targets = dat.analyst_price_targets
        return targets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker/history/{symbol}", tags=["Foreign"])
def ticker_history(symbol: str, period: str = "1mo"):
    """
    Lấy dữ liệu lịch sử giá cổ phiếu theo khoảng thời gian được chỉ định.
    Chức năng: Trả về dữ liệu lịch sử (giá mở, giá đóng, khối lượng, v.v.) của cổ phiếu theo khoảng thời gian 'period' (mặc định là 1 tháng).
    """
    try:
        dat = yf.Ticker(symbol)
        history_data = dat.history(period=period)
        if history_data is not None:
            return history_data.reset_index().to_dict(orient="records")
        else:
            return {"message": "No data available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
