# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TOKENIZERS_PARALLELISM=false \
    TRANSFORMERS_VERBOSITY=error \
    TRANSFORMERS_NO_ADVISORY_WARNINGS=1 \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=none

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY ../Data_And_Config/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files with new structure
COPY ../Core_Application/ ./Core_Application/
COPY ../AI_And_Tools/ ./AI_And_Tools/
COPY ../Data_And_Config/ ./Data_And_Config/

# Set Python path to include all directories
ENV PYTHONPATH="/app:/app/Core_Application:/app/AI_And_Tools"

# Expose ports
EXPOSE 8501 8502 8503

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command to run Streamlit app
CMD ["streamlit", "run", "Core_Application/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
