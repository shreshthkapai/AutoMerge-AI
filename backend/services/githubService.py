import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.user import User
import logging

logger = logging.getLogger(__name__)

async def exchange_code_for_token(code: str) -> str:
    from config.githubApp import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_REDIRECT_URI
    response = requests.post(
        "https://github.com/login/oauth/access_token",
        data={
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": GITHUB_REDIRECT_URI
        },
        headers={"Accept": "application/json"}
    )
    data = response.json()
    return data.get("access_token")

async def store_access_token(db: Session, access_token: str) -> User:
    user_response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_data = user_response.json()
    user = db.query(User).filter(User.id == user_data["id"]).first()
    if not user:
        user = User(id=user_data["id"], github_access_token=access_token)
        db.add(user)
    else:
        user.github_access_token = access_token
    db.commit()
    db.refresh(user)
    logger.info(f"Saved user: {user.id}")
    return user

async def get_user_repos(access_token: str) -> dict:
    # Get user info for username
    user_response = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_data = user_response.json()
    username = user_data["login"]  # Your actual GitHub username (e.g., "shreshthkapai")

    # Get repos
    repo_response = requests.get(
        "https://api.github.com/user/repos",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    repos = repo_response.json()
    return {"username": username, "repos": repos}

async def get_repo_issues(access_token: str, repo_full_name: str, page: int = 1, per_page: int = 30) -> list:
    url = f"https://api.github.com/repos/{repo_full_name}/issues?page={page}&per_page={per_page}"
    logger.info(f"Requesting issues from: {url}")
    
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    logger.info(f"Response status: {response.status_code}")
    
    if response.status_code != 200:
        error_message = f"Failed to fetch issues: {response.text}"
        logger.info(error_message)
        raise HTTPException(status_code=response.status_code, detail=error_message)
    
    issues = response.json()
    logger.info(f"Found {len(issues)} issues")
    
    return issues