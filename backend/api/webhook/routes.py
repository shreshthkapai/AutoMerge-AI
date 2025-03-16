# backend/api/webhook/routes.py
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from config.db import get_db
from models.issue import Issue
from models.user import User
import hmac
import hashlib
import os
import json
from datetime import datetime

router = APIRouter()

# Get the webhook secret from environment variable
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

async def verify_github_webhook(request: Request):
    """Verify the GitHub webhook signature"""
    if not WEBHOOK_SECRET:
        return True  # Skip verification if no secret is set (not recommended for production)
    
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature header")
    
    payload_body = await request.body()
    expected_signature = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    return True

@router.post("/github", dependencies=[Depends(verify_github_webhook)])
async def github_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle GitHub webhook events"""
    payload_body = await request.body()
    event_type = request.headers.get("X-GitHub-Event", "ping")
    payload = json.loads(payload_body)
    
    if event_type == "ping":
        return {"message": "Webhook received successfully"}
    
    if event_type == "issues":
        return await handle_issues_event(payload, db)
    
    # Add more event handlers as needed
    
    return {"message": f"Received {event_type} event"}

async def handle_issues_event(payload: dict, db: Session):
    """Handle GitHub issues events"""
    action = payload.get("action")
    issue_data = payload.get("issue", {})
    repository = payload.get("repository", {})
    
    if action not in ["opened", "edited", "labeled", "unlabeled", "closed", "reopened"]:
        return {"message": f"Ignoring issues.{action} event"}
    
    # Get issue details
    github_issue_id = issue_data.get("id")
    title = issue_data.get("title")
    repo_full_name = repository.get("full_name")
    state = issue_data.get("state")
    html_url = issue_data.get("html_url")
    description = issue_data.get("body")
    
    # Get labels
    labels = [label.get("name") for label in issue_data.get("labels", [])]
    labels_json = json.dumps(labels)
    
    # Check if this is AI fixable (e.g., has bug label)
    is_ai_fixable = "bug" in labels or "ai-fixable" in labels
    
    # Find all users to add this issue for
    users = db.query(User).all()
    
    for user in users:
        # Check if issue already exists for this user
        existing_issue = db.query(Issue).filter(
            Issue.github_issue_id == github_issue_id,
            Issue.user_id == user.id
        ).first()
        
        if existing_issue:
            # Update existing issue
            existing_issue.title = title
            existing_issue.state = state
            existing_issue.description = description
            existing_issue.labels = labels_json
            existing_issue.is_ai_fixable = is_ai_fixable
            existing_issue.updated_at = datetime.now()
        else:
            # Create new issue
            new_issue = Issue(
                github_issue_id=github_issue_id,
                title=title,
                repo_full_name=repo_full_name,
                description=description,
                state=state,
                html_url=html_url,
                is_ai_fixable=is_ai_fixable,
                labels=labels_json,
                user_id=user.id
            )
            db.add(new_issue)
        
    db.commit()
    
    return {"message": f"Successfully processed {action} event for issue #{issue_data.get('number')}"}