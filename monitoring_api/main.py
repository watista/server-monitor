#!/usr/bin/python3

import uvicorn
from fastapi import FastAPI, Request
from config import config
from api.routes import router
from services.logger import logger

# Init API
app = FastAPI()
app.include_router(router, prefix="/api")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request and response."""
    logger.info(f"Received request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


if __name__ == "__main__":

    # Start API
    logger.info("Starting Server Monitor API server")
    uvicorn.run(app, host=config.host_ip, port=int(config.host_port))
