from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from config.db import get_db
from models.user import User
from services.githubService import get_user_repos, get_repo_issues

router = APIRouter()

# Dependency to get user_id from query param
async def get_user_id(user_id: int = 0):  # Default to 0, check below
    if user_id == 0:
        raise HTTPException(status_code=401, detail="Unauthorized - Please provide user_id")
    return user_id

@router.get("/repos")
async def list_repos(db: Session = Depends(get_db), user_id: int = Depends(get_user_id)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    repos = await get_user_repos(user.github_access_token)
    return [{"name": repo["name"], "full_name": repo["full_name"]} for repo in repos["repos"]]

@router.get("/repos/issues")
async def list_issues(
    repo_owner: str = Query(..., description="Repository owner"),
    repo_name: str = Query(..., description="Repository name"),
    db: Session = Depends(get_db), 
    user_id: int = Depends(get_user_id)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    repo_full_name = f"{repo_owner}/{repo_name}"
    issues = await get_repo_issues(user.github_access_token, repo_full_name)
    return [{"id": issue["id"], "title": issue["title"], "number": issue["number"]} for issue in issues]
