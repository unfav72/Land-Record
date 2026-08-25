from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import require_role, hash_password
import models, schemas

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/", response_model=List[schemas.UserResponse])
def list_users(db: Session = Depends(get_db), admin: models.User = Depends(require_role("admin"))):
    return db.query(models.User).all()

@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), admin: models.User = Depends(require_role("admin"))):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    new_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hash_password(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
