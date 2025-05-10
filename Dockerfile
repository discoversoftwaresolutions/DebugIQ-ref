FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy all files to the container
COPY . /app

# Set PYTHONPATH to make top-level modules resolvable
ENV PYTHONPATH=/app

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Start the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
