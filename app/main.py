from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from app.api.deploy import router as deploy_router
from app.api.auth import router as auth_router
from app.api.users import router as user_router
from app.api.service import router as service_router
from app.api.environment import router as environment_router
from app.api.dashboard import router as dashboard_router
from app.api.image import router as image_router
from app.api.namespace import router as ns_router

app = FastAPI(
    title="Release Service",
    description="A detailed description with **Markdown** support",
    version="1.0.0",
    docs_url="/documentation",
    swagger_ui_parameters={
        "docExpansion": "none",          # Collapse all sections by default
        "defaultModelsExpandDepth": -1,  # Hide models section
        "syntaxHighlight": False,        # Disable syntax highlighting
    }
)

# Add this block
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "local-origin.dev", "http://127.0.0.1:3000"],          # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],                               # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],                               # Allow all headers (Authorization, Content-Type, etc.)
)

app.include_router(deploy_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(service_router)
app.include_router(environment_router)
app.include_router(dashboard_router)
app.include_router(image_router)
app.include_router(ns_router)