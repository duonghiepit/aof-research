# Stage build: cài đặt các dependency Python
FROM python:3.9-slim AS builder
WORKDIR /install
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage runtime: cài đặt runtime và các dependency hệ thống cần thiết
FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /install /usr/local
COPY . .
EXPOSE 8501 8000
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port 8000 & streamlit run main.py --server.enableCORS false --server.enableXsrfProtection false"]
