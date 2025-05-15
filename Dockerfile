FROM python:3.10-slim

WORKDIR /app

# Install git for dependencies from Git repositories
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -c "import mcp; print(dir(mcp))"

# Copy application code
COPY . .

# Default port for REST API
EXPOSE 8000

# Default command
CMD ["python", "main.py"]