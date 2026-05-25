# syntax=docker/dockerfile:1.7

# ---------- Builder ----------
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

COPY requirements.txt ./
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt gunicorn

# ---------- Runtime ----------
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production \
    PORT=8000

RUN groupadd --system app && useradd --system --gid app --home /app app
WORKDIR /app

COPY --from=builder /install /usr/local
COPY --chown=app:app . /app

RUN mkdir -p /app/logs /app/.gunicorn && chown -R app:app /app/logs /app/.gunicorn
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request, sys; \
sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status == 200 else 1)"

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers ${GUNICORN_WORKERS:-2} --timeout ${GUNICORN_TIMEOUT:-120} --access-logfile - --error-logfile - --enable-stdio-inheritance wsgi:application"]
