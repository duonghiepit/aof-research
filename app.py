from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from src.data import DataLoader, FinanceLoader
from src.explore.vci.listing import Listing
from src.crawl.scraper import crawl_table_data
import pandas as pd
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

# API để lấy báo cáo tài chính doanh nghiệp
@app.get("/get_finance_business/{symbol}")
async def get_finance_business(symbol: str, start_date: str, end_date: str, data_source: str = "VND"):
    try:
        loader = FinanceLoader(symbol, start_date, end_date, data_source=data_source, minimal=True)
        data_business = loader.get_business_report()
        # Chuyển đổi dữ liệu thành JSON
        data_json = data_business.to_dict(orient="records")
        return JSONResponse(content={"business_report": data_json})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

# API để lấy báo cáo tài chính (Financial Report)
@app.get("/get_finance_report/{symbol}")
async def get_finance_report(symbol: str, start_date: str, end_date: str, data_source: str = "VND"):
    try:
        loader = FinanceLoader(symbol, start_date, end_date, data_source=data_source, minimal=True)
        data_finan = loader.get_finan_report()
        # Chuyển đổi dữ liệu thành JSON
        data_json = data_finan.to_dict(orient="records")
        return JSONResponse(content={"financial_report": data_json})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

# API để lấy báo cáo dòng tiền (Cash Flow Report)
@app.get("/get_cashflow_report/{symbol}")
async def get_cashflow_report(symbol: str, start_date: str, end_date: str, data_source: str = "VND"):
    try:
        loader = FinanceLoader(symbol, start_date, end_date, data_source=data_source, minimal=True)
        data_cash = loader.get_cashflow_report()
        # Chuyển đổi dữ liệu thành JSON
        data_json = data_cash.to_dict(orient="records")
        return JSONResponse(content={"cashflow_report": data_json})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

# API để lấy các chỉ số cơ bản của doanh nghiệp
@app.get("/get_basic_index/{symbol}")
async def get_basic_index(symbol: str, start_date: str, end_date: str, data_source: str = "VND"):
    try:
        loader = FinanceLoader(symbol, start_date, end_date, data_source=data_source, minimal=True)
        data_basic = loader.get_basic_index()
        # Chuyển đổi dữ liệu thành JSON
        data_json = data_basic.to_dict(orient="records")
        return JSONResponse(content={"basic_index": data_json})
    except Exception as e:
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