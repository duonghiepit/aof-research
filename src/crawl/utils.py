# utils.py
from selenium.webdriver.common.by import By
import logging

def flatten_header(table):
    try:
        thead = table.find_element(By.TAG_NAME, "thead")
    except Exception as e:
        logging.error("Không tìm thấy thead: %s", e)
        return []
    header_rows = thead.find_elements(By.TAG_NAME, "tr")
    headers = []
    if len(header_rows) >= 2:
        first_row_cells = header_rows[0].find_elements(By.TAG_NAME, "td")
        second_row_cells = header_rows[1].find_elements(By.TAG_NAME, "td")
        second_index = 0
        for cell in first_row_cells:
            cell_text = cell.text.strip()
            rowspan = cell.get_attribute("rowspan")
            colspan = cell.get_attribute("colspan")
            if rowspan and int(rowspan) > 1:
                headers.append(cell_text)
            else:
                if colspan:
                    for _ in range(int(colspan)):
                        if second_index < len(second_row_cells):
                            second_text = second_row_cells[second_index].text.strip()
                            headers.append(f"{cell_text}_{second_text}")
                            second_index += 1
                        else:
                            headers.append(cell_text)
                else:
                    headers.append(cell_text)
        while second_index < len(second_row_cells):
            headers.append(second_row_cells[second_index].text.strip())
            second_index += 1
    else:
        headers = [cell.text.strip() for cell in header_rows[0].find_elements(By.TAG_NAME, "td")]
    return headers

def get_total_pages(driver):
    """
    Lấy tổng số trang từ các thẻ phân trang (class "pagination-item") bằng cách lấy số lớn nhất.
    """
    try:
        pagination_items = driver.find_elements(By.CLASS_NAME, "pagination-item")
        page_numbers = [int(item.text.strip()) for item in pagination_items if item.text.strip().isdigit()]
        total = max(page_numbers) if page_numbers else 1
        return total
    except Exception as e:
        logging.error("Lỗi khi lấy tổng số trang: %s", e)
        return 1