from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Date, Integer, String, DateTime, Float, Time, func
from models import engine

Base = declarative_base()

# =====================================================
# RESTAURANT
# Floor Master
# =====================================================
class RestaurantFloor(Base):
    __tablename__ = "restaurant_floor"

    id = Column(Integer, primary_key=True, index=True)

    # ---------------- Floor Details ----------------
    floor_code = Column(String(50), nullable=False, index=True)
    # Example: FLR01, BAR01

    floor_name = Column(String(100), nullable=False, index=True)
    # Example: Main Dining, Bar Area

    description = Column(String(255), nullable=True)
    display_order = Column(Integer, nullable=True)

    # ---------------- System Fields ----------------
    status = Column(String(50), nullable=False, index=True, default="ACTIVE")

    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True)

    company_id = Column(String(100), nullable=False, index=True)





Base.metadata.create_all(bind=engine)
