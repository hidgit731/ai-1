FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY server.py /app/server.py
COPY static /app/static

EXPOSE 8000

CMD ["python", "server.py"]
