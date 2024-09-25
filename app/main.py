from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from app.routers import (
    auth,
    user,
    prospect,
    advisor,
    account,
    address,
)  # Add address here
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import os
from app.models.database.schema import Base
from utils.db_connection_manager import engine
import time


app = FastAPI()


# session = get_db()
Base.metadata.create_all(engine)
# session.commit()

app.mount("/static", StaticFiles(directory="./static"), name="static")


@app.get("/")
def health_check():
    return {"status": "Healthy now"}


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(prospect.router)
app.include_router(advisor.router)
app.include_router(account.router)  # Include the account router
app.include_router(address.router)  # Add this line


# Specific exception handlers
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
        content={"detail": "Integrity error: Email already exists"},
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": f"Validation error: {exc.errors()}"},
    )


# Global exception handler for unexpected errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"An unexpected error occurred: {str(exc)}"},
    )


if os.getenv("NESTQ_ENV") != "production":
    origins = [
        "http://localhost:3000"  # React app
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
