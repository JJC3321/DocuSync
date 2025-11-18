"""Main entry point for the Live Document Editor."""
import uvicorn
from src.config import config

if __name__ == "__main__":
    print(f"Starting Live Document Editor on {config.host}:{config.port}")
    print("Open http://localhost:8000 in your browser")
    uvicorn.run("src.api:app", host=config.host, port=config.port, reload=True)
