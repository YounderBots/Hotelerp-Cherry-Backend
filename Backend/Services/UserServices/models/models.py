from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
    Float,
    JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from models import engine
import bcrypt
import uuid

Base = declarative_base()


# =====================================================
# USERS / EMPLOYEES
# =====================================================
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # ================= BASIC =================
    User_Code = Column(String(100), nullable=False, unique=True, index=True)  # Employee ID
    Photo = Column(String(255), nullable=True)

    username = Column(String(100), nullable=False, unique=True, index=True)
    First_Name = Column(String(100), nullable=False, index=True)
    Last_Name = Column(String(100), nullable=False, index=True)

    # ================= CONTACT =================
    Personal_Email = Column(String(100), nullable=False, index=True)
    Company_Email = Column(String(100), nullable=False, unique=True, index=True)
    Password = Column(String(255), nullable=False)

    Mobile = Column(String(20), nullable=False, index=True)
    Alternative_Mobile = Column(String(20), nullable=True)

    # ================= PERSONAL =================
    D_O_B = Column(String(20), nullable=False, index=True)
    Gender = Column(String(20), nullable=False, index=True)
    Marital_Status = Column(String(50), nullable=False, index=True)

    Address = Column(String(255), nullable=False)
    City = Column(String(100), nullable=False, index=True)
    State = Column(String(100), nullable=False, index=True)
    Postal_Code = Column(String(20), nullable=False, index=True)
    Country = Column(String(100), nullable=False, index=True)

    # ================= ORGANIZATION =================
    Department_ID = Column(String(100), nullable=False, index=True)  # dept
    Role_ID = Column(String(100), nullable=False, index=True)        # role
    Shift_ID = Column(String(100), nullable=False, index=True)       # shift

    Date_Of_Joining = Column(String(20), nullable=False, index=True)
    Experience = Column(String(50), nullable=False, index=True)
    Salary_Details = Column(String(100), nullable=False, index=True)
    Register_Code = Column(String(100), nullable=False, index=True)

    # ================= EMERGENCY =================
    Emergency_Name = Column(String(100), nullable=False, index=True)
    Emergency_Contact = Column(String(20), nullable=False, index=True)
    Emergency_Relationship = Column(String(50), nullable=False, index=True)

    # ================= POLICY =================
    Acknowledgment_of_Hotel_Policies = Column(Boolean, default=False)

    # ================= SYSTEM =================
    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)

class Roles(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)
    # ================= SYSTEM =================
    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    company_id = Column(String(100), nullable=False, index=True)

class RolePermissions(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(String(100), nullable=False, index=True)
    menu_id = Column(String(100), nullable=False, index=True)
    submenu_id = Column(String(100), nullable=True, index=True)
    view_permission = Column(Boolean, default=False)
    create_permission = Column(Boolean, default=False)
    edit_permission = Column(Boolean, default=False)
    delete_permission = Column(Boolean, default=False)
    # ================= SYSTEM =================
    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)

class Menus(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    menu_name = Column(String(100), nullable=False, unique=True, index=True)
    menu_link = Column(String(255), nullable=False)
    menu_icon = Column(String(100), nullable=True)
    order = Column(Integer, nullable=False)
    # ================= SYSTEM =================
    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)
    
class Submenus(Base):
    __tablename__ = "submenus"

    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(String(100), nullable=False, index=True)
    submenu_name = Column(String(100), nullable=False, unique=True, index=True)
    submenu_link = Column(String(255), nullable=False)
    # ================= SYSTEM =================
    status = Column(String(100), nullable=False, index=True)
    created_by = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(String(100), nullable=True, index=True)
    company_id = Column(String(100), nullable=False, index=True)

# =====================================================
# CREATE TABLE
# =====================================================
Base.metadata.create_all(bind=engine)
