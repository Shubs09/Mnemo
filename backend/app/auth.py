from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .dependencies import get_current_user
from .supabase_client import supabase


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


class SignupRequest(BaseModel):
    email: str
    password: str


@router.post("/signup")
def signup(request: SignupRequest):
    try:
        response = supabase.auth.sign_up(
            {
                "email": request.email,
                "password": request.password
            }
        )

        return {
            "message": "Signup successful",
            "user": response.user
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/login")
def login(request: SignupRequest):
    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": request.email,
                "password": request.password
            }
        )

        return {
            "message": "Login successful",
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user": response.user
        }

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "user_id": current_user["user"].id,
        "email": current_user["user"].email
    }