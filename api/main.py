from fastapi import FastAPI, HTTPException, Request
import uvicorn
from database.config import API
from fastapi.responses import JSONResponse
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from database.schemas import init_models

from users.auth import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    log = logging.getLogger(__name__)
    log.setLevel(logging.ERROR)
    Path('logs').mkdir(mode=0o774, exist_ok=True)
    logger = logging.getLogger("uvicorn.error")
    handler = RotatingFileHandler(
        "logs/unexpected_exceptions.log",
        mode="a",
        maxBytes = 100*1024,
        backupCount = 3,
    )
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    await init_models()
    yield


app = FastAPI(
    title="Ecoton",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)


@app.exception_handler(HTTPException)
async def error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f'{exc.detail}'}
    )


# port 5017
if __name__ == '__main__':
    app.root_path = '/ecoton'
    uvicorn.run(app, host=API.get('host'), port=API.get('port'))