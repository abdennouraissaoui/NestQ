from fastapi import FastAPI, Request, status, HTTPException, APIRouter
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
import os
import time
from app.routers import (
    auth,
    user,
    prospect,
    advisor,
    account,
    address,
    holding,
    scan,
)
from app.models.database.orm_models import Base
from app.utils.db_connection_manager import engine
from pathlib import Path


app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")


# Create database tables
Base.metadata.create_all(engine)

# Mount static files first
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# API routes
api_router = APIRouter(prefix="/api")
routes = [
    auth.router,
    user.router,
    prospect.router,
    advisor.router,
    account.router,
    address.router,
    scan.router,
    holding.router,
]

for route in routes:
    api_router.include_router(route)


@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": int(time.time())}


app.include_router(api_router)


# Serve index.html for non-file requests
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    static_dir = Path("app/static")
    try:
        # Resolve the full path and ensure it's within the static directory
        file_path = (static_dir / full_path).resolve()
        if not str(file_path).startswith(str(static_dir.resolve())):
            return FileResponse(static_dir / "index.html")

        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(static_dir / "index.html")
    except (ValueError, RuntimeError):
        return FileResponse(static_dir / "index.html")


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"Integrity error: {str(exc)}"},
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": f"Validation error: {exc.errors()}"},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"An unexpected error occurred: {str(exc)}"},
    )


# CORS middleware
if os.getenv("NESTQ_ENV") != "production":
    origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Process time middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
