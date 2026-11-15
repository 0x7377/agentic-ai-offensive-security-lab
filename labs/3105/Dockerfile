FROM python:3.12-alpine

WORKDIR /app
COPY server.py /app/server.py
COPY static /app/static
COPY data /app/data

RUN addgroup -S lab && adduser -S -G lab -u 10001 lab \
    && chown -R lab:lab /app

USER 10001
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=2s --retries=10 CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1
CMD ["python", "/app/server.py"]
