from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.core import database
from app.schemas.enums import LoginMethod
from app.services import user
from app.utils.hash import Hash

router = APIRouter(prefix="/login", tags=["signup/login"])


@router.post("/")
def create_access_token(
    email: str = Body(...),
    password: str = Body(),
    login_method: LoginMethod = Body(),
    db: Session = Depends(database.get_db),
):
    if login_method == LoginMethod.EMAIL:
        if not password or password == "":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials.No password",
            )

        try:
            app_user = user.get_user_by_email(email, db)
            if not app_user or not Hash.verify(password, app_user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )
        except:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials"
            )
    access_token = oauth2.create_access_token({"username": email})
    return {"access_token": access_token, "token_type": "bearer", "user": f"{email}"}
