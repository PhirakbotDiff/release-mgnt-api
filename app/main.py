from fastapi import FastAPI, Request # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from contextlib import asynccontextmanager

import time
import logging

from app.auth.security import init_default_user
from app.auth.init_db import create_tables
from app.api.deploy import router as deploy_router
from app.api.auth import router as auth_router
from app.api.users import router as user_router
from app.api.service import router as service_router
from app.api.environment import router as environment_router
from app.api.dashboard import router as dashboard_router
from app.api.image import router as image_router
from app.api.namespace import router as ns_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    init_default_user()
    yield


app = FastAPI(
    title="Release Service",
    description="A detailed description with **Markdown** support",
    version="1.0.0",
    docs_url="/documentation",
    swagger_ui_parameters={
        "docExpansion": "none",          # Collapse all sections by default
        "defaultModelsExpandDepth": -1,  # Hide models section
        "syntaxHighlight": False,        # Disable syntax highlighting
    },
    lifespan=lifespan
)

# Add this block
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "local-origin.dev", "http://127.0.0.1:3000"],          # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],                               # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],                               # Allow all headers (Authorization, Content-Type, etc.)
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

@app.middleware("http")
async def log_requests(
    request: Request, 
    call_next
):
    start_time = time.time()

    response = await call_next(request)

    user = request.state.user if hasattr(request.state, "user") else None

    process_time = time.time() - start_time
    logger.info(
        "%s %s - %s (%.2f ms) user=%s",
        request.method,
        request.url.path,
        response.status_code,
        process_time * 1000,
        "%s %s" % (user.firstname, user.lastname) if user else "anonymous",
    )

    return response

app.include_router(deploy_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(service_router)
app.include_router(environment_router)
app.include_router(dashboard_router)
app.include_router(image_router)
app.include_router(ns_router)