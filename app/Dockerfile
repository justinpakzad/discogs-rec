FROM python:3.10.6-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY fast_api /app/fast_api
COPY streamlit /app/streamlit
ENV PYTHONPATH="${PYTHONPATH}:/app"


COPY start_api.sh /app/start_api.sh
RUN chmod +x /app/start_api.sh

EXPOSE 8000 8501

CMD ["./start_api.sh"]