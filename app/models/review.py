from app.backend.db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, func
from sqlalchemy.orm import relationship


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String, nullable=True)
    comment_date = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    grade = Column(Float)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")
