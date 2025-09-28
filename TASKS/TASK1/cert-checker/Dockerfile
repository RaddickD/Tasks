# Use Python slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY cert_checker.py .
COPY config.yaml .

# Create non-root user for security
RUN useradd -m -u 1000 certchecker && \
    chown -R certchecker:certchecker /app

# Switch to non-root user
USER certchecker

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check (optional)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

# Default command
ENTRYPOINT ["python", "cert_checker.py"]
CMD ["-c", "config.yaml"]