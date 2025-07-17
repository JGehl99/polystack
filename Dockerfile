# Use official Python image as base
FROM python:3.11-slim

EXPOSE 5000/tcp

# Set working directory
WORKDIR /app

# Copy application code
COPY . /app

# Install system dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt || true

# Set default command to run app.py
CMD ["python", "app.py"]