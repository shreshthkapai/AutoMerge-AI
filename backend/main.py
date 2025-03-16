from fastapi import FastAPI
from api.auth.github import router as auth_router
from api.github.routes import router as github_router
from api.issues.routes import router as issues_router
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
app.include_router(github_router, prefix="/api/github", tags=["github"])
app.include_router(issues_router, prefix="/api/issues", tags=["issues"])

@app.get("/api/")
async def root():
    return {"message": "Welcome to AutoMerge AI!"}