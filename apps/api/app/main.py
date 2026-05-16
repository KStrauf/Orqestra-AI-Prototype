from datetime import UTC, datetime
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.auth import get_current_user
from app.core.config import settings
from app.core.database import Base, engine, get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models import AIAnalysis, BusinessTask, TaskAssignment, User
from app.schemas import *

Base.metadata.create_all(bind=engine)
app = FastAPI(title='OrqestraAI API', version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}

@app.post('/auth/register', status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    user = User(username=req.username, email=req.email, password_hash=hash_password(req.password), role='USER', enabled=True)
    db.add(user)
    try: db.commit()
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(status_code=409, detail='Username or email exists') from exc
    db.refresh(user)
    return {'id': user.id, 'username': user.username, 'email': user.email, 'role': user.role, 'enabled': user.enabled}

@app.post('/auth/login', response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username, User.enabled.is_(True)).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    return TokenResponse(access_token=create_access_token(user.username, user.role), role=user.role)

@app.get('/tasks', response_model=list[BusinessTaskView])
def list_tasks(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(BusinessTask).order_by(BusinessTask.updated_at.desc()).offset(skip).limit(min(limit, 100)).all()

@app.post('/tasks', response_model=BusinessTaskView, status_code=status.HTTP_201_CREATED)
def create_task(req: BusinessTaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = BusinessTask(title=req.title.strip(), description=req.description, work_type=req.work_type, business_area=req.business_area, priority=req.priority, created_by_user_id=user.id)
    db.add(task)
    try: db.commit()
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(status_code=409, detail='Duplicate task shape') from exc
    db.refresh(task); return task

@app.get('/assignments', response_model=list[AssignmentView])
def list_assignments(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(TaskAssignment).order_by(TaskAssignment.updated_at.desc()).offset(skip).limit(min(limit, 100)).all()

@app.post('/assignments', response_model=AssignmentView, status_code=status.HTTP_201_CREATED)
def create_assignment(req: AssignmentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = TaskAssignment(task_id=req.task_id, assigned_to_user_id=req.assigned_to_user_id, assigned_by_user_id=user.id, due_date=req.due_date, priority=req.priority)
    db.add(item)
    try: db.commit()
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(status_code=409, detail='Duplicate same-day assignment') from exc
    db.refresh(item); return item

@app.put('/assignments/{assignment_id}/complete', response_model=AssignmentView)
def complete_assignment(assignment_id: int, req: AssignmentComplete, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    item = db.query(TaskAssignment).filter(TaskAssignment.id == assignment_id).first()
    if not item: raise HTTPException(status_code=404, detail='Assignment not found')
    item.status = 'RESOLVED'; item.completed_at = datetime.now(UTC); item.completion_notes = req.completion_notes
    db.commit(); db.refresh(item); return item

@app.post('/ai/analyze', response_model=AIAnalysisView, status_code=status.HTTP_201_CREATED)
def analyze(req: AIAnalyzeRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    task = db.query(BusinessTask).filter(BusinessTask.id == req.task_id).first()
    if not task: raise HTTPException(status_code=404, detail='Task not found')
    text = f'{task.title} {task.description or ""}'.lower()
    finance = any(t in text for t in ['invoice','payment','vendor','approval','purchase order'])
    analysis = AIAnalysis(task_id=task.id, category='Finance Operations' if finance else 'General Operations', risk_level='MEDIUM' if finance else 'LOW', urgency='HIGH' if 'overdue' in text or 'missing' in text else 'MEDIUM', recommended_priority='HIGH' if finance else 'NORMAL', recommended_owner='Finance Analyst' if finance else 'Operations Coordinator', next_action='Verify approval status and confirm accountable owner before proceeding.', reasoning_summary='Mock analysis based on task language and conservative guardrails.', confidence_score=0.84 if finance else 0.76, guardrail_passed=True, human_review_required=finance)
    db.add(analysis); task.risk_level = analysis.risk_level; task.priority = analysis.recommended_priority; db.commit(); db.refresh(analysis); return analysis

@app.get('/dashboard/summary')
def dashboard(db: Session = Depends(get_db)):
    total = db.query(BusinessTask).count(); high = db.query(BusinessTask).filter(BusinessTask.risk_level.in_(['HIGH','CRITICAL'])).count(); analyses = db.query(AIAnalysis).all()
    avg = round(sum(a.confidence_score for a in analyses)/len(analyses),2) if analyses else 0.0
    return {'totalTasks': total, 'highRiskTasks': high, 'averageConfidence': avg}
