#!/usr/bin/python3

import uvicorn
from fastapi import FastAPI, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from config import config
from api.routes import router, rate_limit_exceeded_handler
from services.logger import logger
from services.db import add_user

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Init API
app = FastAPI()
app.include_router(router, prefix="/api")

# Add Rate Limiting Middleware
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request and response."""
    logger.info(f"Received request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


def main():
    # Add users to database file
    if config.add_users:
        if not config.db_username or not config.db_password:
            logger.error("Both --db-username and --db-password must be provided when using --add-users")
            return

        add_user(config.db_username, config.db_password)
        logger.info(f"User '{config.db_username}' was added successfully to the database.")
        return

    # Start API
    logger.info("Starting Server Monitor API server")
    uvicorn.run(app, host=config.host_ip, port=int(config.host_port))


if __name__ == "__main__":
    main()
