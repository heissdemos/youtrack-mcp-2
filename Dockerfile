FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -c "import fastmcp; print('FastMCP 2.0 installed successfully')"

# Copy application code
COPY . .

# Default port for FastMCP server
EXPOSE 8000

# Default command
CMD ["python", "main.py"]