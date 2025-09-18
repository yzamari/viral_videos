FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY src/microservices/prompt_optimizer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY src/microservices/prompt_optimizer/server.py .

# Expose port
EXPOSE 8001

# Run the service
CMD ["python", "server.py"]