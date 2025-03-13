import httpx
from sqlalchemy.orm import Session
from config.githubApp import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_REDIRECT_URI
from models.user import User

async def exchange_code_for_token(code: str) -> str:
    url = "https://github.com/login/oauth/access_token"
    payload = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": GITHUB_REDIRECT_URI
    }
    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("access_token")

async def store_access_token(db: Session, token: str):
    db_user = User(github_access_token=token)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

async def get_user_repos(token: str):
    url = "https://api.github.com/user/repos"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        repos = response.json()
        username = await get_user_info(token)
        return {"username": username, "repos": repos}
    
# Add the get_user_info function here
async def get_user_info(token: str):
    url = "https://api.github.com/user"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("login")
