FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 LAB_MODE=idor
WORKDIR /app
COPY server.py /app/server.py
COPY static /app/static
RUN addgroup -S lab && adduser -S -G lab -u 10001 lab && chown -R lab:lab /app
USER 10001:10001
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=2s --retries=10 CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1
CMD ["python", "/app/server.py"]

