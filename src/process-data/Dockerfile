FROM python:3.12-slim

WORKDIR /app

# Create logs directory
RUN mkdir -p /app/logs

# Copy application files
COPY requirements.txt .
COPY app/ .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set permissions for logs directory
RUN chmod 777 /app/logs

# Expose port
EXPOSE 8000

# Run the API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]