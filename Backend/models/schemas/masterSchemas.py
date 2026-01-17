from pydantic import BaseModel
from fastapi import Form

class RoomColor(BaseModel):
    room_status: str = Form(...)
    statuscolor: str = Form(...)