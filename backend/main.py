from fastapi import FastAPI
from api.auth.github import router as auth_router
from config.db import Base, engine

app = FastAPI(
    title="AutoMerge AI",
    description="AI-powered GitHub issue fixing with manual review",
    version="0.1.0"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include authentication routes
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

@app.get("/api/")
async def root():
    return {"message": "Welcome to AutoMerge AI!"}