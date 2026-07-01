FROM python:3.13-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY app/ app/

RUN mkdir -p app/static/uploads

EXPOSE 8000

CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "2", \
     "-b", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-"]
