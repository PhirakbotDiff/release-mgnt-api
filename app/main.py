from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.deploy import router as deploy_router
from app.api.auth import router as auth_router

app = FastAPI(title="Release Service")

# Add this block
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],          # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],                               # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],                               # Allow all headers (Authorization, Content-Type, etc.)
)

app.include_router(deploy_router)
app.include_router(auth_router)
