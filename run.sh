lsof -ti:8002 | xargs kill -9
uvicorn api.server:app --reload --port 8002