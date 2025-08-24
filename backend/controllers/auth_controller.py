from fastapi import APIRouter, HTTPException, Depends, Body, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any, Optional
import bcrypt
import logging
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Import from database
from database.repositories.user_repository import (
    get_user_by_username, 
    get_user_by_id,
    create_user as db_create_user
)
from utils.auth_utils import (
    create_access_token,
    get_current_user
)

# Load environment variables
load_dotenv()

# Set up logger
logger = logging.getLogger("tradebot.auth")

router = APIRouter()

# Auth models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: EmailStr

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    balance: float
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        # Check if username already exists
        existing_user = get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Hash the password
        hashed_password = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt()).decode()
        
        # Create user in database
        new_user = db_create_user(user_data.username, hashed_password, user_data.email)
        
        # Convert to response model (exclude password)
        return UserResponse(
            id=new_user["id"],
            username=new_user["username"],
            email=new_user["email"],
            balance=float(new_user["balance"]),
            created_at=new_user["created_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user account"
        )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login a user and return access token"""
    try:
        user = get_user_by_username(form_data.username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Verify password
        is_valid_password = bcrypt.checkpw(
            form_data.password.encode(),
            user["password_hash"].encode()
        )
        
        if not is_valid_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Create access token
        token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": str(user["id"])},
            expires_delta=token_expires
        )
        
        # Create user response (exclude password)
        user_response = UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            balance=float(user["balance"]),
            created_at=user["created_at"]
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_user_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        balance=float(current_user["balance"]),
        created_at=current_user["created_at"]
    )