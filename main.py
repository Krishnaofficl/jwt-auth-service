from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from security import get_current_user, require_role
from database import SessionLocal, get_db
from models import User
from schemas import UserCreate, UserOut
from auth_utils import hash_password, verify_password
from jwt_utils import create_access_token, create_refresh_token, decode_access_token

app = FastAPI(title="JWT Auth Service")


@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/signup", response_model=UserOut, status_code=201)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    db.refresh(new_user)
    return new_user

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": db_user.email, "role": db_user.role})
    refresh_token = create_refresh_token(data={"sub": db_user.email})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

from fastapi import Body

@app.post("/auth/refresh")
def refresh_token(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    payload = decode_access_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    email = payload.get("sub")
    db_user = db.query(User).filter(User.email == email).first()
    if db_user is None:
        raise HTTPException(status_code=401, detail="User not found")

    new_access_token = create_access_token(data={"sub": db_user.email, "role": db_user.role})
    return {"access_token": new_access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/admin/dashboard")
def admin_dashboard(current_user: User = Depends(require_role("admin"))):
    return {"message": f"Welcome, admin {current_user.email}"}