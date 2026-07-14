"""
Authentication router for user login and token generation.
"""
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    """User login request model"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str
    user: Dict[str, Any]


class UserResponse(BaseModel):
    """User response model"""
    id: str
    name: str
    email: str
    role: str


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time delta
    
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify a JWT token.
    
    Args:
        token: JWT token to verify
    
    Returns:
        Decoded token data
    
    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest) -> TokenResponse:
    """
    User login endpoint.
    
    In a production system, this would:
    1. Query a users table to find the user by email
    2. Hash and verify the password using bcrypt
    3. Generate a JWT token with user claims
    
    For now, this accepts any email/password combination for demo purposes.
    To use with real authentication:
    - Implement password hashing with bcrypt
    - Query actual user database
    - Add token blacklist/refresh token mechanism
    
    Args:
        credentials: Login credentials (email and password)
    
    Returns:
        Token and user information
    """
    # In production, verify against actual user database and hashed passwords
    # For demo, accept any email/password
    
    if not credentials.email or not credentials.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    # Create token with user data
    # In production, retrieve actual user data from database
    user_data = {
        "sub": credentials.email,
        "id": "1",
        "name": credentials.email.split("@")[0].title(),
        "email": credentials.email,
        "role": "Sales Representative"
    }
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": credentials.email},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user_data["id"],
            "name": user_data["name"],
            "email": user_data["email"],
            "role": user_data["role"]
        }
    )


@router.get("/verify", response_model=Dict[str, Any])
def verify(token: str) -> Dict[str, Any]:
    """
    Verify a JWT token.
    
    Args:
        token: JWT token to verify
    
    Returns:
        Token validation status
    """
    try:
        payload = verify_token(token)
        return {
            "valid": True,
            "email": payload.get("sub"),
            "exp": payload.get("exp")
        }
    except HTTPException:
        return {
            "valid": False,
            "message": "Token is invalid or expired"
        }
