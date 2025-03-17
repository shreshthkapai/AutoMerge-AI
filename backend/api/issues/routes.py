from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from config.db import get_db
from models.user import User
from models.issue import Issue
from models.fix import Fix
from services.aiService import generate_fix_for_issue, submit_fix_to_github
from typing import List, Optional
from pydantic import BaseModel
import json

router = APIRouter()

class FixCreate(BaseModel):
    content: str
    submission_message: Optional[str] = None

class FixResponse(BaseModel):
    id: int
    content: str
    status: str
    created_at: str
    is_submitted: bool
    submission_message: Optional[str] = None
    pr_url: Optional[str] = None

    class Config:
        orm_mode = True

class IssueResponse(BaseModel):
    id: int
    github_issue_id: int
    title: str
    repo_full_name: str
    description: Optional[str] = None
    state: str
    html_url: Optional[str] = None
    created_at: str
    is_ai_fixable: bool
    labels: Optional[List[str]] = None

    class Config:
        orm_mode = True

class GenerateFixRequest(BaseModel):
    issue_id: int

class SubmitFixRequest(BaseModel):
    submission_message: str

async def get_user_id(user_id: int = Query(..., description="User ID")):
    if user_id == 0:
        raise HTTPException(status_code=401, detail="Unauthorized - Please provide user_id")
    return user_id

@router.get("/issues/{issue_id}/fixes", response_model=List[FixResponse])
async def list_fixes(
    issue_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.user_id == user_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found or not owned by user")
    
    fixes = db.query(Fix).filter(Fix.issue_id == issue_id).all()
    return fixes

@router.post("/issues/{issue_id}/fixes", response_model=FixResponse)
async def create_fix(
    issue_id: int,
    fix_data: FixCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.user_id == user_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found or not owned by user")
    
    fix = Fix(
        issue_id=issue_id,
        content=fix_data.content,
        submission_message=fix_data.submission_message
    )

    db.add(fix)
    db.commit()
    db.refresh(fix)

    return fix

@router.get("/issues", response_model=List[IssueResponse])
async def list_issues(
    search: Optional[str] = None,
    label: Optional[str] = None,
    repo_name: Optional[str] = None,
    is_ai_fixable: Optional[bool] = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = db.query(Issue).filter(Issue.user_id == user_id)

    if search:
        query = query.filter(Issue.title.ilike(f"%{search}%"))

    if repo_name:
        query = query.filter(Issue.repo_full_name.ilike(f"%{repo_name}%"))

    if is_ai_fixable is not None:
        query = query.filter(Issue.is_ai_fixable == is_ai_fixable)

    if label:
        query = query.filter(Issue.labels.ilike(f"%{label}%"))

    issues = query.all()

    for issue in issues:
        if issue.labels:
            try:
                issue.labels = json.loads(issue.labels)
            except:
                issue.labels = []
        else:
            issue.labels = []

    return issues

@router.post("/refresh-ai-status")
async def refresh_ai_fixable_status(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):
    """Refresh AI-fixable status for all user's issues"""
    from services.aiService import update_ai_fixable_status
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_count = await update_ai_fixable_status(db, user_id)
    return {"message": f"Updated {updated_count} issues"}

@router.get("/issues/{issue_id}", response_model=IssueResponse)
async def get_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.user_id == user_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found or not owned by user")
    
    if issue.labels:
        try:
            issue.labels = json.loads(issue.labels)
        except:
            issue.labels = []
    else:
        issue.labels = []

    return issue

@router.post("/issues/{issue_id}/generate-fix", response_model=FixResponse)
async def generate_fix(
    issue_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):
    """Generate an AI fix for an issue"""
    try:
        fix = await generate_fix_for_issue(db, issue_id, user_id)
        return fix
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating fix: {str(e)}")

@router.post("/fixes/{fix_id}/submit", response_model=FixResponse)
async def submit_fix(
    fix_id: int,
    request: SubmitFixRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):
    """Submit a fix to GitHub as a PR"""
    try:
        fix = await submit_fix_to_github(db, fix_id, user_id, request.submission_message)
        return fix
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting fix: {str(e)}")

@router.delete("/fixes/{fix_id}")
async def delete_fix(
    fix_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id)
):
    """Delete a fix"""
    fix = db.query(Fix).filter(Fix.id == fix_id).first()
    if not fix:
        raise HTTPException(status_code=404, detail="Fix not found")
    
    issue = db.query(Issue).filter(Issue.id == fix.issue_id, Issue.user_id == user_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found or not owned by user")
    
    db.delete(fix)
    db.commit()
    
    return {"message": "Fix deleted successfully"}