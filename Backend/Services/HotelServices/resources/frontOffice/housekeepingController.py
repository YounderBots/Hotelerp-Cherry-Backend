from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime

from resources.utils import verify_authentication
from models import get_db, models
from configs.base_config import CommonWords

router = APIRouter()
 
