from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.core import database
from app.schemas.enums import LoginMethod
from app.services import user as user_service
from app.utils.hash import Hash
from app.utils.logger import logger

router = APIRouter(prefix="/login", tags=["signup/login"])


@router.post("/")
def create_access_token(
    email: str = Body(...),
    password: str = Body(None),
    login_method: LoginMethod = Body(...),
    db: Session = Depends(database.get_db),
):
    if login_method == LoginMethod.EMAIL:
        if not password or password == "":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials.No password",
            )

        try:
            app_user = user_service.get_user_by_email(email, db)
            if not app_user or not Hash.verify(password, app_user.password):
<<<<<<< HEAD
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        except Exception:
            logger.error(f"Login attempt with invalid credentials ({email})")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
=======
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )
        except:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials"
            )
>>>>>>> 62d5304c3a0d622f0b8bfad986e3b07621fd51fd
    else:
        user = user_service.get_user_by_email(email, db).first()
        if not user:
            pass

    access_token = oauth2.create_access_token({"username": email})
    return {"access_token": access_token, "token_type": "bearer", "user": f"{email}"}
