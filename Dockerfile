# GlucoShield CDSS - Production Container Image
# FUSE AI-201 Capstone | Module 6

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8501

WORKDIR /app

# Install system dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and models
COPY src/ ./src/
COPY models/ ./models/
COPY plots/ ./plots/
COPY monitoring/ ./monitoring/
COPY evaluation/ ./evaluation/
COPY app.py .
COPY run_full_pipeline.py .
COPY download_data.py .

# Expose Streamlit default port (8501) and API port (8000)
EXPOSE 8501 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command: launch interactive Streamlit CDSS prototype
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

