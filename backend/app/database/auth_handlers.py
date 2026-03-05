from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.database.config import get_db
from app.models.user import User
from app.utils.verify_token import verify_supabase_token


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> UUID:
    token = credentials.credentials

    payload = verify_supabase_token(token)

    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = UUID(payload["sub"])

    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        try:
            db.add(User(id=user_id))
            db.commit()
        except IntegrityError:
            db.rollback()

    return user_id





