from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
import logging

from database.repositories.user_repository import get_user_by_id

# Load environment variables
load_dotenv()

# Set up logger
logger = logging.getLogger("tradebot.auth")

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/auth/login",
    auto_error=False  # Don't auto-raise errors for missing tokens
)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data (dict): Data to encode in the token
        expires_delta (Optional[timedelta]): Token expiration time
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get the current authenticated user
    
    Args:
        token (str): JWT token
        
    Returns:
        Dict[str, Any]: User data
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception
        
    user = get_user_by_id(int(user_id))
    
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[Dict[str, Any]]:
    """
    Get the current authenticated user if a token is provided, otherwise return None
    
    Args:
        token (Optional[str]): JWT token
        
    Returns:
        Optional[Dict[str, Any]]: User data or None
    """
    if not token:
        return None
        
    try:
        user = await get_current_user(token)
        return user
    except HTTPException:
        return None