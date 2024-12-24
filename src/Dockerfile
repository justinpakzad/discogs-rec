FROM python:3.10.6-slim

WORKDIR /src

RUN apt-get update && apt-get install -y \
    build-essential \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /src/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py /src/main.py
COPY preprocessing.py /src/preprocessing.py


CMD ["python" ,"main.py"]