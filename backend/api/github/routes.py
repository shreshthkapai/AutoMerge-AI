from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from config.db import get_db
from models.user import User
import requests
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

@router.get("/repos/all-issues")
async def list_all_issues(
    db: Session = Depends(get_db), 
    user_id: int = Depends(get_user_id),
    include_forked_sources: bool = Query(True, description="Include issues from original repositories of forks")
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    all_issues = []
    processed_repos = set()  # Track which repos we've already processed
    
    # First, get all detailed information about user's repositories
    try:
        # Get basic repo info
        repos_response = requests.get(
            "https://api.github.com/user/repos?type=all&sort=updated",
            headers={"Authorization": f"Bearer {user.github_access_token}"}
        )
        repos = repos_response.json()
        
        # Process each repository
        for repo in repos:
            if "full_name" in repo:
                repo_full_name = repo["full_name"]
                processed_repos.add(repo_full_name.lower())
                
                # Get issues from this repo
                try:
                    issues = await get_repo_issues(user.github_access_token, repo_full_name)
                    for issue in issues:
                        issue["repository"] = {
                            "name": repo["name"],
                            "full_name": repo_full_name,
                            "is_fork": repo.get("fork", False)
                        }
                    all_issues.extend(issues)
                except Exception as e:
                    print(f"Error fetching issues for {repo_full_name}: {str(e)}")
                
                # If it's a fork and we want to include original repo issues
                if include_forked_sources and repo.get("fork", False):
                    # Get detailed fork info to find the parent/source repo
                    try:
                        fork_detail_response = requests.get(
                            f"https://api.github.com/repos/{repo_full_name}",
                            headers={"Authorization": f"Bearer {user.github_access_token}"}
                        )
                        fork_detail = fork_detail_response.json()
                        
                        # Check if parent/source info is available
                        if "parent" in fork_detail and "full_name" in fork_detail["parent"]:
                            parent_full_name = fork_detail["parent"]["full_name"]
                            
                            # Only process if we haven't seen this repo before
                            if parent_full_name.lower() not in processed_repos:
                                processed_repos.add(parent_full_name.lower())
                                
                                try:
                                    parent_issues = await get_repo_issues(user.github_access_token, parent_full_name)
                                    for issue in parent_issues:
                                        issue["repository"] = {
                                            "name": fork_detail["parent"]["name"],
                                            "full_name": parent_full_name,
                                            "is_fork": False,
                                            "is_parent_of_fork": True
                                        }
                                    all_issues.extend(parent_issues)
                                except Exception as e:
                                    print(f"Error fetching issues for parent repo {parent_full_name}: {str(e)}")
                    except Exception as e:
                        print(f"Error fetching fork details for {repo_full_name}: {str(e)}")
    except Exception as e:
        print(f"Error fetching user repos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching repositories: {str(e)}")
    
    return [
        {
            "id": issue["id"], 
            "title": issue["title"], 
            "number": issue["number"],
            "repository": issue["repository"],
            "html_url": issue.get("html_url", ""),
            "state": issue.get("state", ""),
            "created_at": issue.get("created_at", "")
        } 
        for issue in all_issues
    ]
