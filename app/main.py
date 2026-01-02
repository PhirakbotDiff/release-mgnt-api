from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.deploy import router as deploy_router
from app.api.auth import router as auth_router
from app.api.users import router as user_router

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
    allow_origins=["http://localhost:3000", "local-origin.dev", "http://10.20.60.104:3000"],          # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],                               # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],                               # Allow all headers (Authorization, Content-Type, etc.)
)

app.include_router(deploy_router)
app.include_router(auth_router)
app.include_router(user_router)