from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.logging_config import setup_logging
from app.tasks.router import router as tasks_router
from app.users.router import router as users_router

setup_logging()

app = FastAPI(title="Task Tracker")

app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ALLOW_ORIGINS, allow_credentials=True,
                   allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"], allow_headers=["Content-Type"])

app.include_router(users_router)
app.include_router(tasks_router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"message": exc.errors()[0]["msg"]})
