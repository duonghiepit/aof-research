# AOF Stock Research

Repo này chứa các tài liệu nghiên cứu, mã nguồn và công cụ liên quan đến dự án **AOF Research**. Mục tiêu của dự án là thu thập, phân tích và trình bày các kết quả nghiên cứu về thu thập dữ liệu chứng khoán tại Việt Nam và thế giới.

## Nội dung chính

- **Tài liệu nghiên cứu:** Tổng hợp các bài báo, báo cáo và tài liệu tham khảo liên quan đến chủ đề nghiên cứu.
- **Mã nguồn:** Các script, module và công cụ hỗ trợ xử lý dữ liệu, mô phỏng và phân tích kết quả.
- **Bài báo và báo cáo:** Các bài viết trình bày kết quả nghiên cứu, bao gồm cả các báo cáo thí nghiệm và phân tích dữ liệu.

## Cài đặt

### Yêu cầu hệ thống

- Hệ điều hành: Linux/MacOS/Windows
- Phiên bản Python: ≥ 3.7
- Docker (nếu chạy với Docker)

## Cấu trúc repo

Dưới đây là cấu trúc thư mục chính trong dự án:

```
AOF-RESEARCH/
├── __pycache__/               # Thư mục cache tự động sinh ra của Python
├── aof_research.egg-info/     # Thông tin gói (egg) khi cài đặt Python package
├── build/                     # Thư mục build (tạo sẵn nếu cần đóng gói)
├── dist/                      # Thư mục chứa các gói (package) sau khi build
├── env/                       # Môi trường ảo (virtual environment) đã được tạo
├── src/                       # Mã nguồn chính của dự án
├── .dockerignore              # Danh sách file/thư mục bỏ qua khi build Docker image
├── app.py                     # File chứa ứng dụng FastAPI (API)
├── Dockerfile                 # File cấu hình để build Docker image
├── main.py                    # File chứa giao diện Streamlit (UI)
├── README.md                  # Hướng dẫn sử dụng và thông tin về dự án
├── requirements.txt           # Danh sách các thư viện Python cần thiết
└── setup.py                   # File cấu hình để đóng gói dự án (nếu muốn tạo package)
```

## Hướng dẫn sử dụng

### 1. Chạy mã nguồn trên local

1. **Thiết lập môi trường ảo:**

   ```bash
   python -m venv env
   # Kích hoạt môi trường ảo:
   # Windows:
   .\env\Scripts\activate
   # Linux/MacOS:
   # source env/bin/activate
   ```

2. **Cài đặt các thư viện cần thiết:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Chạy ứng dụng API với Uvicorn:**

   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```
   - Truy cập FastAPI API docs tại: [http://localhost:8000/docs](http://localhost:8000/docs)

4. **Chạy giao diện người dùng với Streamlit:**

   ```bash
   streamlit run main.py
   ```
   - Truy cập giao diện website tại: [http://localhost:8501/](http://localhost:8501/)

### 2. Chạy dự án với Docker

1. **Tải image từ Docker Hub (nếu đã được đẩy sẵn):**

   ```bash
   docker pull duonghiepit/stock-aof-research
   ```

2. **Chạy container Docker:**

   ```bash
   docker run -d -p 8501:8501 -p 8000:8000 duonghiepit/stock-aof-research
   ```
   - API sẽ chạy trên cổng 8000 (FastAPI API docs: [http://localhost:8000/docs](http://localhost:8000/docs))  
   - UI website sẽ chạy trên cổng 8501 ([http://localhost:8501/](http://localhost:8501/))

   > Lưu ý: Đảm bảo rằng các cổng này không bị xung đột với ứng dụng khác trên hệ thống của bạn.

### 3. Các chức năng chính

- **FastAPI** (app.py): Cung cấp các endpoint cho API, có thể kiểm thử bằng `/docs`.
- **Streamlit** (main.py): Cung cấp giao diện web đơn giản để tương tác, xem dữ liệu hoặc trực quan hóa.

## Đóng góp

Nếu bạn muốn đóng góp vào dự án này, hãy làm theo các bước sau:

1. Fork repo này.
2. Tạo branch mới cho tính năng hoặc bản sửa lỗi của bạn:  
   ```bash
   git checkout -b feature/ten-tinh-nang
   ```
3. Commit các thay đổi của bạn:  
   ```bash
   git commit -m "Mô tả thay đổi"
   ```
4. Push lên branch của bạn:  
   ```bash
   git push origin feature/ten-tinh-nang
   ```
5. Tạo Pull Request với mô tả chi tiết về các thay đổi của bạn.

## Liên hệ

Nếu có thắc mắc hoặc cần hỗ trợ, vui lòng liên hệ qua:
- Email: duonghiep59.it@gmail.com
- GitHub: duonghiepit

## Giấy phép

Repo này được cấp phép theo [MIT License](LICENSE).