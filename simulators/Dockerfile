# Industrial Data Simulator Docker Image
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy simulator code
COPY industrial_simulator.py .

# Create log directory
RUN mkdir -p /var/log/industrial

# Environment variables
ENV KAFKA_BOOTSTRAP_SERVERS=kafka:9092
ENV OTEL_ENDPOINT=http://otel-collector:4318
ENV SIMULATOR_TYPE=scada
ENV METRICS_PORT=8080
ENV DATA_RATE_PER_SEC=100

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${METRICS_PORT}/health')"

# Run simulator
CMD ["python", "-u", "industrial_simulator.py"]
