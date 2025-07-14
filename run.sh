#!/bin/bash

# Kill any existing process on port 8002
echo "Stopping any existing traffic-sync service..."
lsof -ti:8002 | xargs kill -9 2>/dev/null || true

# Wait a moment for cleanup
sleep 2

echo "Starting traffic-sync service..."
echo "Press Ctrl+C to stop the service gracefully"

# Start the service with proper signal handling
trap 'echo "Received interrupt signal, shutting down..."; exit 0' INT TERM

uvicorn api.server:app --reload --port 8002