FROM python:3.12-alpine

WORKDIR /app
COPY server.py /app/server.py
COPY static /app/static

EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --retries=5 CMD wget -q -O - http://127.0.0.1:8080/healthz || exit 1
CMD ["python", "/app/server.py"]
