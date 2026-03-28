# Use Alpine for minimal size and reduced attack surface
FROM python:3.11-alpine

# Create non-root user
RUN adduser -D -u 1000 backenduser && \
    mkdir -p /app && \
    chown -R backenduser:backenduser /app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

USER backenduser

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8001/health', timeout=2)"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]