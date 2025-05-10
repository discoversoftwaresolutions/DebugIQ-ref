FROM python:3.11-slim

WORKDIR /app
COPY . /app

ENV PYTHONPATH=/app

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
