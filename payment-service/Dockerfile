FROM python:3.12

WORKDIR /payment-service

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH /app

CMD ["python", "/app/bin/main.py"]
