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

# Run the bot
CMD ["python", "main.py"]