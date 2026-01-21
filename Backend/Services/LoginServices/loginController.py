from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from datetime import timedelta
import bcrypt

from models import models, get_db
from configs.base_config import BaseConfig, CommonWords
from resources.utils import create_access_token

router = APIRouter()

# =====================================================
# LOGIN (REACT)
# =====================================================
@router.post("/login", status_code=status.HTTP_200_OK)
def login(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    user = db.query(models.Employee_Data).filter(
        models.Employee_Data.Company_Email == email,
        models.Employee_Data.status == CommonWords.STATUS
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid email"
        )

    if not bcrypt.checkpw(password.encode("utf-8"), user.Password.encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )

    access_token_expires = timedelta(
        minutes=BaseConfig.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = create_access_token(
        data={
            "user_id": user.id,
            "company_id": user.company_id
        },
        expires_delta=access_token_expires
    )

    return {
        "status": "success",
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.First_Name if hasattr(user, "First_Name") else None,
            "email": user.Company_Email,
            "company_id": user.company_id
        }
    }


# =====================================================
# LOGOUT (REACT)
# =====================================================
@router.post("/logout", status_code=status.HTTP_200_OK)
def logout():
    """
    JWT is stateless.
    Frontend should remove token from storage.
    """
    return {
        "status": "success",
        "message": "Logged out successfully"
    }
