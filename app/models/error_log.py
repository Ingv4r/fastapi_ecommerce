from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from app.backend.db import Base


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True)
    path = Column(String)
    method = Column(String)
    status_code = Column(Integer)
    error_message = Column(String)
    timestamp = Column(DateTime, default=datetime.now())
