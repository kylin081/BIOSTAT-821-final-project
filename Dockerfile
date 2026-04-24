# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Initialize the database
RUN python db/seed.py

# Expose port 8000
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
