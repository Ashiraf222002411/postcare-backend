FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 5001

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=5001

# Start the application
CMD ["python", "sms-service/app/enhanced_sms_service.py"]