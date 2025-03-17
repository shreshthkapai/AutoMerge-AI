import requests
from fastapi import HTTPException
from models.fix import Fix
from models.issue import Issue
from models.user import User
from datetime import datetime
import json
import re

async def is_issue_ai_fixable(issue):
    """
    Determine if an issue is fixable by AI based on:
    1. Has 'bug' or 'ai-fixable' labels
    2. Contains error messages or stack traces
    3. Has clear reproduction steps
    """
    # Check labels
    labels = []
    if issue.labels:
        try:
            labels = json.loads(issue.labels)
        except:
            pass
    
    if "bug" in labels or "ai-fixable" in labels:
        return True
        
    # Check content for error patterns if description exists
    if issue.description:
        # Check for stack traces or error messages
        error_patterns = [
            r"error:",
            r"exception:",
            r"traceback",
            r"fail(ed|ure|ing)?",
            r"steps to reproduce"
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, issue.description, re.IGNORECASE):
                return True
    
    return False

async def update_ai_fixable_status(db, user_id=None):
    """Update is_ai_fixable status for all issues or for a specific user"""
    query = db.query(Issue)
    if user_id:
        query = query.filter(Issue.user_id == user_id)
    
    issues = query.all()
    updated_count = 0
    
    for issue in issues:
        fixable = await is_issue_ai_fixable(issue)
        if issue.is_ai_fixable != fixable:
            issue.is_ai_fixable = fixable
            updated_count += 1
    
    if updated_count > 0:
        db.commit()
    
    return updated_count

async def generate_fix_for_issue(db, issue_id, user_id):
    """
    Generate an AI-powered fix for a specific issue
    """
    # Fetch the issue
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.user_id == user_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found or not owned by user")
    
    # Check if the issue is AI-fixable
    if not issue.is_ai_fixable:
        raise HTTPException(status_code=400, detail="This issue is not marked as AI-fixable")
    
    # In a real implementation, you would call your AI model or service here
    # For this example, we'll generate a simple mock fix
    fix_content = f"""
    # AI-generated fix for issue #{issue.github_issue_id}
    
    This is a placeholder for an AI-generated code fix. In a production environment,
    this would contain actual code changes to address the issue.
    
    For a bug related to {issue.title}, we might:
    1. Identify the root cause
    2. Implement a fix that addresses the core issue
    3. Add tests to verify the solution
    
    ## Suggested Changes:
    ```python
    def fix_bug():
        # Previous buggy code
        # return broken_result
        
        # New fixed code
        return correct_result
    ```
    """
    
    # Create a new fix record
    fix = Fix(
        issue_id=issue_id,
        content=fix_content,
        status="pending",
        created_at=datetime.now(),
        is_submitted=False
    )
    
    db.add(fix)
    db.commit()
    db.refresh(fix)
    
    return fix

async def submit_fix_to_github(db, fix_id, user_id, submission_message):
    """
    Submit a fix to GitHub as a pull request
    """
    # Fetch the fix
    fix = db.query(Fix).filter(Fix.id == fix_id).first()
    if not fix:
        raise HTTPException(status_code=404, detail="Fix not found")
    
    # Fetch the issue
    issue = db.query(Issue).filter(Issue.id == fix.issue_id, Issue.user_id == user_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found or not owned by user")
    
    # Fetch the user to get GitHub token
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # In a real implementation, you would:
    # 1. Create a new branch
    # 2. Apply the fix to the code
    # 3. Commit the changes
    # 4. Create a pull request
    
    # For this example, we'll just update the fix status
    fix.is_submitted = True
    fix.submission_message = submission_message
    fix.pr_url = f"https://github.com/{issue.repo_full_name}/pull/999"  # Mock PR URL
    fix.status = "submitted"
    
    db.commit()
    db.refresh(fix)
    
    return fix