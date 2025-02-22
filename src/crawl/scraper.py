# scraper.py
import time
import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm

from .utils import flatten_header, get_total_pages

# Cấu hình logging: mức INFO sẽ hiển thị thông tin tiến trình vào console.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def crawl_table_data(symbol: str):
    """
    Crawl dữ liệu bảng từ trang chứng khoán dựa trên mã symbol.
    Trả về DataFrame và tổng số trang (theo phân trang).
    """
    url = f"https://cafef.vn/du-lieu/lich-su-giao-dich-{symbol}-1.chn#data"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    
    all_data = []
    header_columns = None
    current_page = 0

    try:
        driver.get(url)
        # Đợi bảng xuất hiện
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "owner-contents-table"))
        )
        time.sleep(1)  # Cho thêm chút thời gian load dữ liệu
        total_pages = get_total_pages(driver)
        logging.info("Tổng số trang theo phân trang: %s", total_pages)
        
        header_columns = flatten_header(table)
        logging.info("Header: %s", header_columns)
        
        # Vòng lặp chuyển trang cho đến khi không tìm thấy nút next hoặc nút bị ẩn
        while True:
            current_page += 1
            print("Đang crawl: {}/{}".format(current_page, total_pages))
            
            table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "owner-contents-table"))
            )
            tbody = table.find_element(By.TAG_NAME, "tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                row_data = [cell.text.strip() for cell in cells]
                if len(row_data) == len(header_columns):
                    all_data.append(row_data)
                else:
                    logging.warning("Dòng dữ liệu không khớp header: %s", row_data)
            
            try:
                btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "paging-right"))
                )
            except Exception:
                logging.info("Không tìm thấy nút next. Kết thúc crawl.")
                break
            
            btn_class = btn.get_attribute("class")
            if "enable" in btn_class:
                logging.info("Nút next đã bị ẩn. Kết thúc crawl.")
                break
            
            old_tbody_html = tbody.get_attribute("innerHTML")
            ActionChains(driver).move_to_element(btn).click().perform()
            WebDriverWait(driver, 10).until(
                lambda d: d.find_element(By.ID, "owner-contents-table")
                          .find_element(By.TAG_NAME, "tbody").get_attribute("innerHTML") != old_tbody_html
            )
    except Exception as e:
        logging.error("Lỗi: %s", e)
    finally:
        driver.quit()
    
    df = pd.DataFrame(all_data, columns=header_columns)
    return df, total_pages