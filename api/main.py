"""Backward-compatible FastAPI entrypoint."""

from src.api.main import *  # noqa: F401,F403


if __name__ == "__main__":
    import uvicorn
    from config.settings import API_HOST, API_PORT

    uvicorn.run(app, host=API_HOST, port=API_PORT)
