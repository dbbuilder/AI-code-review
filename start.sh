#!/bin/bash
# Railway startup script with PORT handling

# Default PORT to 8080 if not set
export PORT=${PORT:-8080}

echo "Starting AutoRev API on port $PORT"

# Run uvicorn with Python to ensure PORT is properly read
exec python -m src.api.main
