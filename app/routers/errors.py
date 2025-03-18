from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette import status

from app.backend.db_depends import get_db
from app.models.error_log import ErrorLog

router = APIRouter(prefix="/error", tags=["error"])


@router.post("/test", status_code=status.HTTP_400_BAD_REQUEST)
async def generate_error():
    raise HTTPException(status_code=400, detail="Тестовая ошибка")


@router.get("/logs", status_code=status.HTTP_200_OK)
async def get_error_logs(db: Annotated[Session, Depends(get_db)]):
    logs = db.scalars(select(ErrorLog)).all()

    return {
        "logs": [
            {
                "path": log.path,
                "method": log.method,
                "status_code": log.status_code,
                "message": log.error_message,
                "timestamp": log.timestamp.isoformat(),
            }
            for log in logs
        ]
    }
