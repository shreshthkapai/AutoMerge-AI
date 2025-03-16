# backend/main.py
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from api.auth.github import router as github_auth_router
from api.github.routes import router as github_router
from api.issues.routes import router as issues_router
from api.webhook.routes import router as webhook_router
from config.db import Base, engine

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AutoMerge AI")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you should set this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create main router
main_router = APIRouter(prefix="/api")

# Add our routers
main_router.include_router(github_auth_router, prefix="/auth", tags=["Authentication"])
main_router.include_router(github_router, prefix="/github", tags=["GitHub"])
main_router.include_router(issues_router, prefix="/issues", tags=["Issues"])
main_router.include_router(webhook_router, prefix="/webhook", tags=["Webhooks"])

# Add the main router to the app
app.include_router(main_router)

@app.get("/api/")
async def root():
    return {"message": "Welcome to AutoMerge AI"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)