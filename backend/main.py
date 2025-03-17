from fastapi import FastAPI, APIRouter, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from api.auth.github import router as github_auth_router
from api.github.routes import router as github_router
from api.issues.routes import router as issues_router
from api.webhook.routes import router as webhook_router
from config.db import Base, engine, SessionLocal
from services.aiService import update_ai_fixable_status
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_env():
    required_vars = [
        "DATABASE_URL", 
        "GITHUB_CLIENT_ID", 
        "GITHUB_CLIENT_SECRET",
        "GITHUB_REDIRECT_URI"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

async def startup_ai_status_update():
    """Update AI-fixable status for all issues on startup"""
    db = SessionLocal()
    try:
        logger.info("Running initial AI-fixable status update")
        await update_ai_fixable_status(db)
        logger.info("AI-fixable status update completed")
    finally:
        db.close()

# Call this before creating the app
validate_env()
Base.metadata.create_all(bind=engine)
app = FastAPI(title="AutoMerge AI")

# Configure CORS
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",  # Common React port
    os.getenv("FRONTEND_URL", ""),  # Production frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins[2] else ["*"],  # Use specific origins if configured, otherwise allow all
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

@app.on_event("startup")
async def startup_event(background_tasks: BackgroundTasks):
    # Run AI-fixable status update in background
    background_tasks.add_task(startup_ai_status_update)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)