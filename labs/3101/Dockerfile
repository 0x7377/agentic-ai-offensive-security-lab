FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    LAB_DB_PATH=/tmp/lab-3101.db

WORKDIR /app
COPY server.py /app/server.py
COPY static /app/static

RUN addgroup -S lab && adduser -S -G lab -u 10001 lab \
    && chown -R lab:lab /app

USER 10001:10001
EXPOSE 8080

HEALTHCHECK --interval=5s --timeout=2s --start-period=5s --retries=10 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=1)"

CMD ["python", "/app/server.py"]
