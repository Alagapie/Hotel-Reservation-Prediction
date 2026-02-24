# Use Python slim as base image
FROM python:3.11-slim

# Avoid writing pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Optional: Run training pipeline (if needed during image build)
# You might remove this for CI/CD; better to train separately
# RUN python pipeline/training_pipeline.py

# Expose the port your app runs on
EXPOSE 80

# Run your app
CMD ["python", "application.py"]