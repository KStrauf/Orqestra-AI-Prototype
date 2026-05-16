from datetime import datetime, date
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30), default='USER')
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

class BusinessTask(Base):
    __tablename__ = 'business_tasks'
    __table_args__ = (UniqueConstraint('created_by_user_id', 'title', 'business_area', name='uq_task_shape'),)
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(160), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    work_type: Mapped[str | None] = mapped_column(String(80), index=True)
    business_area: Mapped[str | None] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(30), default='PENDING', index=True)
    priority: Mapped[str] = mapped_column(String(30), default='NORMAL', index=True)
    risk_level: Mapped[str] = mapped_column(String(30), default='LOW', index=True)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

class TaskAssignment(Base):
    __tablename__ = 'task_assignments'
    __table_args__ = (UniqueConstraint('task_id', 'assigned_to_user_id', 'due_date', name='uq_assignment_once'),)
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('business_tasks.id', ondelete='CASCADE'), index=True)
    assigned_to_user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    assigned_by_user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    due_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30), default='PENDING', index=True)
    priority: Mapped[str] = mapped_column(String(30), default='NORMAL', index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    completion_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

class AIAnalysis(Base):
    __tablename__ = 'ai_analysis'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('business_tasks.id', ondelete='CASCADE'), index=True)
    category: Mapped[str] = mapped_column(String(80), index=True)
    risk_level: Mapped[str] = mapped_column(String(30), index=True)
    urgency: Mapped[str] = mapped_column(String(30), index=True)
    recommended_priority: Mapped[str] = mapped_column(String(30), index=True)
    recommended_owner: Mapped[str] = mapped_column(String(80))
    next_action: Mapped[str] = mapped_column(Text)
    reasoning_summary: Mapped[str] = mapped_column(Text)
    confidence_score: Mapped[float] = mapped_column(Float)
    guardrail_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    human_review_required: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
