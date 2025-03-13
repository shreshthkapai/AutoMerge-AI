from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from config.githubApp import GITHUB_CLIENT_ID, GITHUB_REDIRECT_URI
from services.githubService import exchange_code_for_token, store_access_token, get_user_repos
from config.db import get_db
from models.user import User

router = APIRouter()

@router.get("/github/login")
async def github_login():
    github_auth_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={GITHUB_CLIENT_ID}&"
        f"redirect_uri={GITHUB_REDIRECT_URI}&"
        f"scope=repo"
    )
    return RedirectResponse(url=github_auth_url)

@router.get("/github/callback")
async def github_callback(code: str, db: Session = Depends(get_db)):
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    
    try:
        access_token = await exchange_code_for_token(code)
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to obtain access token")
        
        user = await store_access_token(db, access_token)
        # Redirect to frontend with user_id
        frontend_url = f"http://localhost:5173/?user_id={user.id}"
        return RedirectResponse(url=frontend_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

@router.get("/repos/{user_id}")
async def get_repos(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        data = await get_user_repos(user.github_access_token)
        return {
            "username": data["username"],
            "repos": [{"name": repo["name"], "full_name": repo["full_name"]} for repo in data["repos"]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching repos: {str(e)}")