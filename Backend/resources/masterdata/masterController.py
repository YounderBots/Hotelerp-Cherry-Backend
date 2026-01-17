from fastapi import APIRouter, Depends,UploadFile,status, Request, Form ,File 
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse,JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional
from configs import BaseConfig
from datetime import  timedelta 
from models import get_db, models
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from resources.utils import create_access_token
from starlette.middleware.sessions import SessionMiddleware
import bcrypt,uuid,shutil
from icecream import ic
from jose import jwt, JWTError

from configs.base_config import BaseConfig,CommonWords


router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/master_data")
async def master_data(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                room_type_data = db.query(models.Room_Type).filter(models.Room_Type.status==CommonWords.STATUS).all()
                for i in room_type_data:
                    comp_data = db.query(models.Room_Complementry).filter(models.Room_Complementry.id==i.Complementry,models.Room_Complementry.status==CommonWords.STATUS).first()
                    if comp_data:
                        i.complementry_name = comp_data.Complementry_Name
                complementry_data = db.query(models.Room_Complementry).filter(models.Room_Complementry.status==CommonWords.STATUS).all()
                return templates.TemplateResponse('master_data/HOTEL/master_data.html', context={'request': request,'color_theme':color_theme,'room_type_data':room_type_data,'complementry_data':complementry_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#==============================================>>>. Facility     
@router.get("/facilities")
async def facilities_home_page(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                facilites_data = db.query(models.Facility).filter(models.Facility.status==CommonWords.STATUS).all()
                return templates.TemplateResponse('master_data/HOTEL/facilities.html', context={'request': request,'color_theme':color_theme,'facilites_data':facilites_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/facilities")
async def facilities_post(request: Request,db: Session = Depends(get_db),facility_name:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.Facility).filter(func.lower(models.Facility.Facility_Name) ==facility_name.lower()).filter(models.Facility.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    facility = models.Facility(Facility_Name=facility_name,status=CommonWords.STATUS,created_by=created_by,company_id=company_id)
                    db.add(facility)
                    db.commit()
                    db.refresh(facility)
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/facilities_id/{table_id}")
async def facilities_id_taking(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                facilites_data = db.query(models.Facility).filter(models.Facility.id==table_id).filter(models.Facility.status==CommonWords.STATUS).first()
                return JSONResponse(content=jsonable_encoder(facilites_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/update_facilities")
async def facilities_update(request: Request,db: Session = Depends(get_db),edit_id:int=Form(...),edit_facility_name:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.Facility).filter(models.Facility.id!=edit_id,func.lower(models.Facility.Facility_Name) == edit_facility_name.lower()).filter(models.Facility.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    db.query(models.Facility).filter(models.Facility.id==edit_id).update({'Facility_Name':edit_facility_name})
                    db.commit()
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/delete_facility/{table_id}")
async def deleting_facilities_data(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                db.query(models.Facility).filter(models.Facility.id==table_id).update({'status':CommonWords.UNSTATUS})
                db.commit()
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


#=====================================>>> Room Type
#Room Type endpoints
@router.get("/room_type")
async def room_type_home_page(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                room_type_data = db.query(models.Room_Type).filter(models.Room_Type.status==CommonWords.STATUS).all()
                for i in room_type_data:
                    comp_data = db.query(models.Room_Complementry).filter(
                        models.Room_Complementry.id==i.Complementry,
                        models.Room_Complementry.status==CommonWords.STATUS
                    ).first()
                    if comp_data:
                        i.complementry_name = comp_data.Complementry_Name
                complementry_data = db.query(models.Room_Complementry).filter(
                    models.Room_Complementry.status==CommonWords.STATUS
                ).all()
                return templates.TemplateResponse('master_data/HOTEL/room_type.html', 
                    context={
                        'request': request,
                        'color_theme':color_theme,
                        'room_type_data':room_type_data,
                        'complementry_data':complementry_data
                    })
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/room_type")
async def room_type_post(
    request: Request,
    db: Session = Depends(get_db),
    room_typ:str=Form(...),
    room_cost:str=Form(...),
    bed_cost:str=Form(...),
    complementry:str=Form(...),
    daily_rate:str=Form(None),
    weekly_rate:str=Form(None),
    bed_only_rate:str=Form(None),
    bed_breakfast_rate:str=Form(None),
    half_board_rate:str=Form(None),
    full_board_rate:str=Form(None)
):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.Room_Type).filter(
                    func.lower(models.Room_Type.Type_Name) == room_typ.lower(),
                    models.Room_Type.status==CommonWords.STATUS
                ).all()
                if not check_previous_data:
                    new_room_type = models.Room_Type(
                        Type_Name=room_typ,
                        Room_Cost=room_cost,
                        Bed_Cost=bed_cost,
                        Complementry=complementry,
                        Daily_Rate=daily_rate,
                        Weekly_Rate=weekly_rate,
                        Bed_Only_Rate=bed_only_rate,
                        Bed_And_Breakfast_Rate=bed_breakfast_rate,
                        Half_Board_Rate=half_board_rate,
                        Full_Board_Rate=full_board_rate,
                        status=CommonWords.STATUS,
                        created_by=created_by,
                        company_id=company_id
                    )
                    db.add(new_room_type)
                    db.commit()
                    db.refresh(new_room_type)
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/room_type_id/{table_id}")
async def room_type_id_taking(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                room_type_data = db.query(models.Room_Type).filter(
                    models.Room_Type.id==table_id,
                    models.Room_Type.status==CommonWords.STATUS
                ).first()
                return JSONResponse(content=jsonable_encoder(room_type_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/update_room_type")
async def room_type_update(
    request: Request,
    db: Session = Depends(get_db),
    edit_id:int=Form(...),
    edit_room_typ:str=Form(...),
    edit_room_cost:str=Form(...),
    edit_bed_cost:str=Form(...),
    edit_complementry:str=Form(...),
    edit_daily_rate:str=Form(None),
    edit_weekly_rate:str=Form(None),
    edit_bed_only_rate:str=Form(None),
    edit_bed_breakfast_rate:str=Form(None),
    edit_half_board_rate:str=Form(None),
    edit_full_board_rate:str=Form(None)
):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.Room_Type).filter(
                    models.Room_Type.id!=edit_id,
                    func.lower(models.Room_Type.Type_Name) == edit_room_typ.lower(),
                    models.Room_Type.status==CommonWords.STATUS
                ).all()
                if not check_previous_data:
                    db.query(models.Room_Type).filter(models.Room_Type.id==edit_id).update({
                        'Type_Name': edit_room_typ,
                        'Room_Cost': edit_room_cost,
                        'Bed_Cost': edit_bed_cost,
                        'Complementry': edit_complementry,
                        'Daily_Rate': edit_daily_rate,
                        'Weekly_Rate': edit_weekly_rate,
                        'Bed_Only_Rate': edit_bed_only_rate,
                        'Bed_And_Breakfast_Rate': edit_bed_breakfast_rate,
                        'Half_Board_Rate': edit_half_board_rate,
                        'Full_Board_Rate': edit_full_board_rate
                    })
                    db.commit()
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/delete_room_type/{table_id}")
async def deleting_room_type_data(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                db.query(models.Room_Type).filter(models.Room_Type.id==table_id).update({'status':CommonWords.UNSTATUS})
                db.commit()
                return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
#=====================================>>> Bed Type
@router.get("/bed_type")
async def bed_type_home_page(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                bed_type_data = db.query(models.Bed_Type).filter(models.Bed_Type.status==CommonWords.STATUS).all()
                return templates.TemplateResponse('master_data/HOTEL/bed_type.html', context={'request': request,'color_theme':color_theme,'bed_type_data':bed_type_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/bed_type")
async def bed_type_post(request: Request,db: Session = Depends(get_db),bed_typ:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.Bed_Type).filter(func.lower(models.Bed_Type.Type_Name) == bed_typ.lower()).filter(models.Bed_Type.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    new_bed_type = models.Bed_Type(Type_Name=bed_typ,status=CommonWords.STATUS,created_by=created_by,company_id=company_id)
                    db.add(new_bed_type)
                    db.commit()
                    db.refresh(new_bed_type)
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/bed_type_id/{table_id}")
async def bed_type_taking(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                bed_type_data = db.query(models.Bed_Type).filter(models.Bed_Type.id==table_id).filter(models.Bed_Type.status==CommonWords.STATUS).first()
                return JSONResponse(content=jsonable_encoder(bed_type_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/update_bed_type")
async def bed_type_update(request: Request,db: Session = Depends(get_db),edit_id:int=Form(...),edit_bed_typ:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.Bed_Type).filter(models.Bed_Type.id!=edit_id,func.lower(models.Bed_Type.Type_Name) == edit_bed_typ.lower()).filter(models.Bed_Type.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    db.query(models.Bed_Type).filter(models.Bed_Type.id==edit_id).update({'Type_Name':edit_bed_typ})
                    db.commit()
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/delete_bed_type/{table_id}")
async def deleting_bed_type_data(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                db.query(models.Bed_Type).filter(models.Bed_Type.id==table_id).update({'status':CommonWords.UNSTATUS})
                db.commit()
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#=====================================>>> Hall / Floor
@router.get("/hall_floor")
async def hall_floor_home_page(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                hall_data = db.query(models.TableHallNames).filter(models.TableHallNames.status==CommonWords.STATUS).all()
                return templates.TemplateResponse('master_data/HOTEL/hall.html', context={'request': request,'color_theme':color_theme,'hall_data':hall_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/hall_floor")
async def hall_floor_post(request: Request,db: Session = Depends(get_db),hall_name:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.TableHallNames).filter(func.lower(models.TableHallNames.hall_name)==hall_name.lower()).filter(models.TableHallNames.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    new_hall = models.TableHallNames(hall_name=hall_name,status=CommonWords.STATUS,created_by=created_by,company_id=company_id)
                    db.add(new_hall)
                    db.commit()
                    db.refresh(new_hall)
                    return JSONResponse(content=jsonable_encoder('OK'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_208_ALREADY_REPORTED)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/hall_floor_data_info/{table_id}")
async def get_a_hall_floor_info(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                particular_data = db.query(models.TableHallNames).filter(models.TableHallNames.id==table_id).filter(models.TableHallNames.status==CommonWords.STATUS).first()
                return JSONResponse(content=jsonable_encoder(particular_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/update_hall_floor")
async def update_hall_floor_post(request: Request,db: Session = Depends(get_db),edit_id:int=Form(...),edit_hall_name:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.TableHallNames).filter(models.TableHallNames.id!=edit_id,func.lower(models.TableHallNames.hall_name)==edit_hall_name.lower()).filter(models.TableHallNames.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    db.query(models.TableHallNames).filter(models.TableHallNames.id==edit_id).update({'hall_name':edit_hall_name})                    
                    db.commit()
                    return JSONResponse(content=jsonable_encoder('OK'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_208_ALREADY_REPORTED)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/delete_hall_floor_id/{table_id}")
async def deleting_hall_floor_info(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                db.query(models.TableHallNames).filter(models.TableHallNames.id==table_id).update({'status':CommonWords.UNSTATUS})
                db.commit()
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#=====================================>>> Rooms
@router.get("/room")
async def room_home_page(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                bed_type_data = db.query(models.Bed_Type).filter(models.Bed_Type.status==CommonWords.STATUS).all()
                room_type_data = db.query(models.Room_Type).filter(models.Room_Type.status==CommonWords.STATUS).all()
                room_data = db.query(models.Room).filter(models.Room.status==CommonWords.STATUS).all()
                return templates.TemplateResponse('master_data/HOTEL/room.html', context={'request': request,'color_theme':color_theme,'room_data':room_data,
                                                                                          'bed_type_data':bed_type_data,'room_type_data':room_type_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/room")
async def room_post(request: Request,db: Session = Depends(get_db),room_no:str=Form(...),room_name:str=Form(...),room_type:str=Form(...),bed_type:str=Form(...),tele_no:str=Form(...),max_adult:str=Form(...),max_child:str=Form(...),addimgfile:UploadFile=File(...),addimgfile1:UploadFile=File(...),addimgfile2:UploadFile=File(...),addimgfile3:UploadFile=File(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.Room).filter(models.Room.Room_No==room_no).filter(models.Room.status==CommonWords.STATUS).all()
                if not check_previous_data:
                
                    file_type = addimgfile.content_type
                    file_type1 = addimgfile1.content_type
                    file_type2 = addimgfile2.content_type
                    file_type3 = addimgfile3.content_type
                    extention1 = file_type.split('/')[-1]
                    extention2 = file_type1.split('/')[-1]
                    extention3 = file_type2.split('/')[-1]
                    extention4 = file_type3.split('/')[-1]

                    image_file1 = str(uuid.uuid4())+ '.' + str(extention1)
                    image_file2 = str(uuid.uuid4())+ '.' + str(extention2)
                    image_file3 = str(uuid.uuid4())+ '.' + str(extention3)
                    image_file4 = str(uuid.uuid4())+ '.' + str(extention4)
                    
                    with open(f"./templates/static/upload_image/{image_file1}", "wb+") as file_object_1:
                        shutil.copyfileobj(addimgfile.file, file_object_1)
                        
                    with open(f"./templates/static/upload_image/{image_file2}", "wb+") as file_object_2:
                        shutil.copyfileobj(addimgfile1.file, file_object_2)
                    
                    with open(f"./templates/static/upload_image/{image_file3}", "wb+") as file_object_3:
                        shutil.copyfileobj(addimgfile2.file, file_object_3)
                    
                    with open(f"./templates/static/upload_image/{image_file4}", "wb+") as file_object_4:
                        shutil.copyfileobj(addimgfile3.file, file_object_4)
                        
                        
                    new_room = models.Room(Room_No=room_no,Room_Name=room_name,Room_Type_ID=room_type,Bed_Type_ID=bed_type,
                                           Room_Telephone=tele_no,Max_Adult_Occupy=max_adult,Max_Child_Occupy=max_child,Room_Booking_status= CommonWords.AVAILABLE,
                                           Room_Working_status = CommonWords.WORK_STATUS,Room_Status=CommonWords.Room_Condition,status=CommonWords.STATUS,created_by=created_by,company_id=company_id,
                                           Room_Image_1=image_file1,Room_Image_2=image_file2,Room_Image_3=image_file3,Room_Image_4=image_file4)
                
                    db.add(new_room)
                    db.commit()
                    db.refresh(new_room)

                    return JSONResponse(content=jsonable_encoder('OK'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_208_ALREADY_REPORTED)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/room_image_view/{table_id}")
async def get_a_room_image_info(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                particular_data = db.query(models.Room).filter(models.Room.id==table_id).filter(models.Room.status==CommonWords.STATUS).first()
                return JSONResponse(content=jsonable_encoder(particular_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/room_data_info/{table_id}")
async def get_a_room_info(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                particular_data = db.query(models.Room).filter(models.Room.id==table_id).filter(models.Room.status==CommonWords.STATUS).first()
                return JSONResponse(content=jsonable_encoder(particular_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/update_room")
async def update_room_post(request: Request,db: Session = Depends(get_db),edit_id:int=Form(...),edit_room_no:str=Form(...),edit_room_name:str=Form(...),edit_room_type:str=Form(...),edit_bed_type:str=Form(...),edit_tele_no:str=Form(...),edit_max_adult:str=Form(...),edit_max_child:str=Form(...),edit_room_condition:str=Form(...),edit_image_1:Optional[UploadFile]=File(None),edit_image_2:Optional[UploadFile]=File(None),edit_image_3:Optional[UploadFile]=File(None),edit_image_4:Optional[UploadFile]=File(None)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                
                check_previous_data = db.query(models.Room).filter(models.Room.id!=edit_id,models.Room.Room_No==edit_room_no).filter(models.Room.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    
                    particular_data = db.query(models.Room).filter(models.Room.id==edit_id).filter(models.Room.status==CommonWords.STATUS).first()
                    
                    def give_extentions_and_name(image_name,old_image_name):
                        file_type = image_name.content_type
                        extension = file_type.split('/')[-1]
                        old_image_name = old_image_name.split('.')[0]
                        return str(old_image_name)+'.'+str(extension)

                    if(edit_image_1!=None):
                        image_file1 = give_extentions_and_name(edit_image_1,particular_data.Room_Image_1)
                        with open(f"./templates/static/upload_image/{image_file1}", "wb+") as file_object_1:
                            shutil.copyfileobj(edit_image_1.file, file_object_1)
                            db.query(models.Room).filter(models.Room.id==edit_id).update({'Room_Image_1':image_file1})
                            db.commit()
                            
                    if(edit_image_2!=None):
                        image_file2 = give_extentions_and_name(edit_image_2,particular_data.Room_Image_2)
                        with open(f"./templates/static/upload_image/{image_file2}", "wb+") as file_object_2:
                            shutil.copyfileobj(edit_image_2.file, file_object_2)
                            db.query(models.Room).filter(models.Room.id==edit_id).update({'Room_Image_2':image_file2})
                            db.commit()
                            
                    if(edit_image_3!=None):
                        image_file3 = give_extentions_and_name(edit_image_3,particular_data.Room_Image_3)
                        with open(f"./templates/static/upload_image/{image_file3}", "wb+") as file_object_3:
                            shutil.copyfileobj(edit_image_3.file, file_object_3)
                            db.query(models.Room).filter(models.Room.id==edit_id).update({'Room_Image_3':image_file3})
                            db.commit()
                            
                    if(edit_image_4!=None):
                        image_file4 = give_extentions_and_name(edit_image_4,particular_data.Room_Image_4)
                        with open(f"./templates/static/upload_image/{image_file4}", "wb+") as file_object_4:
                            shutil.copyfileobj(edit_image_4.file, file_object_4)
                            db.query(models.Room).filter(models.Room.id==edit_id).update({'Room_Image_4':image_file4})
                            db.commit()
                    
                    db.query(models.Room).filter(models.Room.id==edit_id).update({'Room_No':edit_room_no,'Room_Name':edit_room_name,
                                                                                  'Room_Type_ID':edit_room_type,'Bed_Type_ID':edit_bed_type,
                                                                                  'Room_Telephone':edit_tele_no,'Max_Adult_Occupy':edit_max_adult,
                                                                                  'Max_Child_Occupy':edit_max_child,'Room_Status':edit_room_condition})                    
                    db.commit()
                    return JSONResponse(content=jsonable_encoder('OK'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_208_ALREADY_REPORTED)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/delete_room_id/{table_id}")
async def deleting_room_info(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                db.query(models.Room).filter(models.Room.id==table_id).update({'status':CommonWords.UNSTATUS})
                db.commit()
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
#=====================================>>> Identity Proof
@router.get("/identity_proof")
async def identity_proof_home_page(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                ids_type_data = db.query(models.Identity_Proofs).filter(models.Identity_Proofs.status==CommonWords.STATUS).all()
                return templates.TemplateResponse('master_data/HOTEL/identity_proof.html', context={'request': request,'color_theme':color_theme,'ids_type_data':ids_type_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/identity_proof")
async def identity_proof_post(request: Request,db: Session = Depends(get_db),proof_name:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.Identity_Proofs).filter(func.lower(models.Identity_Proofs.Proof_Name) == proof_name.lower()).filter(models.Identity_Proofs.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    new_identity_type = models.Identity_Proofs(Proof_Name=proof_name,status=CommonWords.STATUS,created_by=created_by,company_id=company_id)
                    db.add(new_identity_type)
                    db.commit()
                    db.refresh(new_identity_type)
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/identity_proof_id/{table_id}")
async def identity_proof_taking(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                identity_type_data = db.query(models.Identity_Proofs).filter(models.Identity_Proofs.id==table_id).filter(models.Identity_Proofs.status==CommonWords.STATUS).first()
                return JSONResponse(content=jsonable_encoder(identity_type_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/update_identity_proof")
async def identity_proof_update(request: Request,db: Session = Depends(get_db),edit_id:int=Form(...),edit_proof:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.Identity_Proofs).filter(models.Identity_Proofs.id!=edit_id,func.lower(models.Identity_Proofs.Proof_Name) == edit_proof.lower()).filter(models.Identity_Proofs.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    db.query(models.Identity_Proofs).filter(models.Identity_Proofs.id==edit_id).update({'Proof_Name':edit_proof})
                    db.commit()
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/delete_identity_proof/{table_id}")
async def deleting_identity_proof_data(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                db.query(models.Identity_Proofs).filter(models.Identity_Proofs.id==table_id).update({'status':CommonWords.UNSTATUS})
                db.commit()
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#=====================================>>> country and Currency 
@router.get("/country_courrency")
async def country_courrency_home_page(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                country_data = db.query(models.Country_Courrency).filter(models.Country_Courrency.status==CommonWords.STATUS).all()
                return templates.TemplateResponse('master_data/HOTEL/currency_country.html', context={'request': request,'color_theme':color_theme,'country_data':country_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/country_courrency")
async def country_courrency_post(request: Request,db: Session = Depends(get_db),count_name:str=Form(...),cury_symbol:str=Form(...),cury_name:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.Country_Courrency).filter(func.lower(models.Country_Courrency.Country_Name) == count_name.lower()).filter(models.Country_Courrency.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    new_country = models.Country_Courrency(Country_Name=count_name,Courrency_Name=cury_name,Symbol=cury_symbol,status=CommonWords.STATUS,created_by=created_by,company_id=company_id)
                    db.add(new_country)
                    db.commit()
                    db.refresh(new_country)
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/country_courrency_id/{table_id}")
async def country_courrency_taking(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                country_data = db.query(models.Country_Courrency).filter(models.Country_Courrency.id==table_id).filter(models.Country_Courrency.status==CommonWords.STATUS).first()
                return JSONResponse(content=jsonable_encoder(country_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/update_country_courrency")
async def country_courrency_update(request: Request,db: Session = Depends(get_db),edit_id:int=Form(...),edit_count_name:str=Form(...),edit_cury_symbol:str=Form(...),edit_cury_name:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.Country_Courrency).filter(models.Country_Courrency.id!=edit_id,func.lower(models.Country_Courrency.Country_Name) == edit_count_name.lower()).filter(models.Country_Courrency.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    db.query(models.Country_Courrency).filter(models.Country_Courrency.id==edit_id).update({'Country_Name':edit_count_name,'Courrency_Name':edit_cury_name,'Symbol':edit_cury_symbol})
                    db.commit()
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/delete_country_courrency/{table_id}")
async def deleting_country_courrency_data(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                db.query(models.Country_Courrency).filter(models.Country_Courrency.id==table_id).update({'status':CommonWords.UNSTATUS})
                db.commit()
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#=====================================>>> discount 
@router.get("/discount")
async def discount_home_page(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                discount_data = db.query(models.Discount_Data).filter(models.Discount_Data.status==CommonWords.STATUS).all()
                country_data = db.query(models.Country_Courrency).filter(models.Country_Courrency.status==CommonWords.STATUS).all()
                return templates.TemplateResponse('master_data/HOTEL/discount.html', context={'request': request,'color_theme':color_theme,
                                                                                              'discount_data':discount_data,'country_data':country_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/discount")
async def discount_post(request: Request,db: Session = Depends(get_db),count_name:str=Form(...),discnt:str=Form(...),percen:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.Discount_Data).filter(func.lower(models.Discount_Data.Country_ID) == count_name.lower(),func.lower(models.Discount_Data.Discount_Name) == discnt.lower()).filter(models.Discount_Data.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    new_discount = models.Discount_Data(Country_ID=count_name,Discount_Name=discnt,Discount_Percentage=percen,status=CommonWords.STATUS,created_by=created_by,company_id=company_id)
                    db.add(new_discount)
                    db.commit()
                    db.refresh(new_discount)
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/discount_id/{table_id}")
async def discount_taking(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                discount_data = db.query(models.Discount_Data).filter(models.Discount_Data.id==table_id).filter(models.Discount_Data.status==CommonWords.STATUS).first()
                return JSONResponse(content=jsonable_encoder(discount_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/update_discount")
async def discount_update(request: Request,db: Session = Depends(get_db),edit_id:int=Form(...),edit_count_name:str=Form(...),edit_discnt:str=Form(...),edit_percen:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.Discount_Data).filter(models.Discount_Data.id!=edit_id,func.lower(models.Discount_Data.Country_ID) == edit_count_name.lower(),func.lower(models.Discount_Data.Discount_Name) == edit_discnt.lower()).filter(models.Discount_Data.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    db.query(models.Discount_Data).filter(models.Discount_Data.id==edit_id).update({'Country_ID':edit_count_name,'Discount_Name':edit_discnt,'Discount_Percentage':edit_percen})
                    db.commit()
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/delete_discount/{table_id}")
async def deleting_discount_data(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                db.query(models.Discount_Data).filter(models.Discount_Data.id==table_id).update({'status':CommonWords.UNSTATUS})
                db.commit()
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#=====================================>>> Tax 
@router.get("/tax")
async def tax_home_page(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                tax_data = db.query(models.Tax_type).filter(models.Tax_type.status==CommonWords.STATUS).all()
                country_data = db.query(models.Country_Courrency).filter(models.Country_Courrency.status==CommonWords.STATUS).all()
                return templates.TemplateResponse('master_data/HOTEL/tax.html', context={'request': request,'color_theme':color_theme,
                                                                                              'tax_data':tax_data,'country_data':country_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/tax")
async def tax_post(request: Request,db: Session = Depends(get_db),count_name:str=Form(...),tax_name:str=Form(...),percen:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.Tax_type).filter(func.lower(models.Tax_type.Country_ID) == count_name.lower(),func.lower(models.Tax_type.Tax_Name) == tax_name.lower()).filter(models.Tax_type.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    new_tax = models.Tax_type(Country_ID=count_name,Tax_Name=tax_name,Tax_Percentage=percen,status=CommonWords.STATUS,created_by=created_by,company_id=company_id)
                    db.add(new_tax)
                    db.commit()
                    db.refresh(new_tax)
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/tax_id/{table_id}")
async def tax_taking(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                tax_data = db.query(models.Tax_type).filter(models.Tax_type.id==table_id).filter(models.Tax_type.status==CommonWords.STATUS).first()
                return JSONResponse(content=jsonable_encoder(tax_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/update_tax")
async def tax_update(request: Request,db: Session = Depends(get_db),edit_id:int=Form(...),edit_count_name:str=Form(...),edit_tax:str=Form(...),edit_percen:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.Tax_type).filter(models.Tax_type.id!=edit_id,func.lower(models.Tax_type.Country_ID) == edit_count_name.lower(),func.lower(models.Tax_type.Tax_Name) == edit_tax.lower()).filter(models.Tax_type.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    db.query(models.Tax_type).filter(models.Tax_type.id==edit_id).update({'Country_ID':edit_count_name,'Tax_Name':edit_tax,'Tax_Percentage':edit_percen})
                    db.commit()
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/delete_tax/{table_id}")
async def deleting_tax_data(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                db.query(models.Tax_type).filter(models.Tax_type.id==table_id).update({'status':CommonWords.UNSTATUS})
                db.commit()
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
#=====================================>>> Payment Methods
@router.get("/payment_methods")
async def payment_methods_home_page(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                payment_data = db.query(models.Payment_Methods).filter(models.Payment_Methods.status==CommonWords.STATUS).all()
                return templates.TemplateResponse('master_data/HOTEL/payment.html', context={'request': request,'color_theme':color_theme,'payment_data':payment_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/payment_methods")
async def post_payment_methods(request: Request,db: Session = Depends(get_db),payment:str=Form()):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.Payment_Methods).filter(func.lower(models.Payment_Methods.payment_method) ==payment.lower()).filter(models.Payment_Methods.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    new_payment = models.Payment_Methods(payment_method=payment,status=CommonWords.STATUS,created_by=created_by,company_id=company_id)
                    db.add(new_payment)
                    db.commit()
                    db.refresh(new_payment)
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
@router.get("/payment_methods_id/{table_id}")
async def payment_methods_id_taking(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                payment_data = db.query(models.Payment_Methods).filter(models.Payment_Methods.id==table_id).filter(models.Payment_Methods.status==CommonWords.STATUS).first()
                return JSONResponse(content=jsonable_encoder(payment_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/update_payment_methods")
async def payment_methods_update(request: Request,db: Session = Depends(get_db),edit_id:int=Form(...),edit_payment:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse("../login/login", status_scode=status.HTTP_307_TEMPORARY_REDIRECT)  
            else:
                check_previous_data = db.query(models.Payment_Methods).filter(models.Payment_Methods.id!=edit_id,func.lower(models.Payment_Methods.payment_method) == edit_payment.lower()).filter(models.Payment_Methods.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    db.query(models.Payment_Methods).filter(models.Payment_Methods.id==edit_id).update({'payment_method':edit_payment})
                    db.commit()
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/delete_payment_methods/{table_id}")
async def deleting_payment_methods_data(request: Request,table_id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                db.query(models.Payment_Methods).filter(models.Payment_Methods.id==table_id).update({'status':CommonWords.UNSTATUS})
                db.commit()
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#=====================================>>> Quantity
@router.get("/quantity")
async def Quantity_home_page(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                quantity_data = db.query(models.Quantity).filter(models.Quantity.status==CommonWords.STATUS).all()
                return templates.TemplateResponse('master_data/quantity.html', context={'request': request,'color_theme':color_theme,'quantity_data':quantity_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.post('/post_qun')
async def create_qun(request:Request,db:Session=Depends(get_db),name:str=Form(...)):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                statuss = "ACTIVE"
                created_by = "1"
                company_id = ""
                find=db.query(models.Quantity).filter(models.Quantity.Name==name,models.Quantity.status=="ACTIVE").first()
                if find is None:
                    body=models.Quantity(Name=name,created_by=created_by,company_id=company_id,updated_at="",status=CommonWords.STATUSs)
                    db.add(body)
                    db.commit()
                    error = "Successfully Inserted"
                    json_compatible_item_data = jsonable_encoder(error)
                    return JSONResponse(content=error)
                else:
                    error = "Already this name Exist"
                    json_compatible_item_data = jsonable_encoder(error)
                    return JSONResponse(content=error)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 


@router.put('/put_qun/{id}')
async def view_qun(request:Request,id:int,db:Session=Depends(get_db)):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                
                body=db.query(models.Quantity).filter(models.Quantity.id==id).first()
                json_compatible_item_data = jsonable_encoder(body)
                return JSONResponse(content=json_compatible_item_data)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 

@router.post('/update_qun')
async def update_qun(request:Request,db:Session=Depends(get_db),edit_id:int=Form(...),edit_name:str=Form(...)):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                find=db.query(models.Quantity).filter(models.Quantity.id != edit_id,models.Quantity.name == edit_name,models.Quantity.status=="ACTIVE").first()

                if find is None:
                    
                    db.query(models.Quantity).filter(models.Quantity.id==edit_id).update({"name":edit_name})
                    db.commit()
                    error = "Successfully Inserted"
                    json_compatible_item_data = jsonable_encoder(error)
                    return JSONResponse(content=error)
                else:
                    error = "Already this name Exist"
                    json_compatible_item_data = jsonable_encoder(error)
                    return JSONResponse(content=error)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 

@router.get('/delete_qun/{id}')
def del_qun(request:Request,id:int,db:Session=Depends(get_db)):
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                db.query(models.Quantity).filter(models.Quantity.id == id).update({"status":"INACTIVE"})
                db.commit()
                error = "Successfully Updated"
                json_compatible_item_data = jsonable_encoder(error)
                return JSONResponse(content=error)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 


#=====================================>>> Assign Task Type
@router.get("/task_type")
async def Task_type_home_page(request: Request, db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status == CommonWords.STATUS).first()
                task_type_data = db.query(models.Task_Type).filter(models.Task_Type.status == CommonWords.STATUS).all()
                return templates.TemplateResponse('master_data/HOTEL/task_type.html', 
                    context={'request': request, 'color_theme': color_theme, 'task_type_data': task_type_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/task_type")
async def Task_type_post(
    request: Request, 
    db: Session = Depends(get_db),
    task_typ: str = Form(...),
    task_color: str = Form(...)
):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                # Check if task type already exists
                check_previous_data = db.query(models.Task_Type).filter(
                    models.Task_Type.Type_Name == task_typ,
                    models.Task_Type.status == CommonWords.STATUS
                ).first()
                
                if not check_previous_data:
                    new_task_type = models.Task_Type(
                        Type_Name=task_typ,
                        Color=task_color,
                        status=CommonWords.STATUS,
                        created_by=created_by,
                        company_id=company_id
                    )
                    db.add(new_task_type)
                    db.commit()
                    db.refresh(new_task_type)
                    return JSONResponse(content=jsonable_encoder('Ok'), status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(
                        content=jsonable_encoder('Error'), 
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/task_type_id/{table_id}")
async def task_type_taking(request: Request, table_id: int, db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                task_type_data = db.query(models.Task_Type).filter(
                    models.Task_Type.id == table_id,
                    models.Task_Type.status == CommonWords.STATUS
                ).first()
                if task_type_data:
                    return JSONResponse(
                        content=jsonable_encoder(task_type_data),
                        status_code=status.HTTP_200_OK
                    )
                return JSONResponse(
                    content=jsonable_encoder({"error": "Task type not found"}),
                    status_code=status.HTTP_404_NOT_FOUND
                )
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/update_task_type")
async def Task_type_update(
    request: Request, 
    db: Session = Depends(get_db),
    edit_id: int = Form(...),
    edit_task_typ: str = Form(...),
    edit_task_color: str = Form(...)
):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                # Check if another task type with same name exists
                check_previous_data = db.query(models.Task_Type).filter(
                    models.Task_Type.id != edit_id,
                    models.Task_Type.Type_Name == edit_task_typ,
                    models.Task_Type.status == CommonWords.STATUS
                ).first()
                
                if not check_previous_data:
                    db.query(models.Task_Type).filter(models.Task_Type.id == edit_id).update({
                        'Type_Name': edit_task_typ,
                        'Color': edit_task_color
                    })
                    db.commit()
                    return JSONResponse(content=jsonable_encoder('Ok'), status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(
                        content=jsonable_encoder('Error'), 
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/delete_task_type/{table_id}")
async def deleting_task_type_data(request: Request, table_id: int, db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM])
            created_by: str = payload.get("user_id")
            company_id: str = payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                # Soft delete by updating status
                result = db.query(models.Task_Type).filter(
                    models.Task_Type.id == table_id,
                    models.Task_Type.status == CommonWords.STATUS
                ).update({'status': CommonWords.UNSTATUS})
                
                db.commit()
                
                if result == 0:
                    return JSONResponse(
                        content={"error": "Task type not found or already deleted"},
                        status_code=status.HTTP_404_NOT_FOUND
                    )
                return JSONResponse(
                    content={"message": "Task type deleted successfully"},
                    status_code=status.HTTP_200_OK
                )
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#=====================================>>> Room Complementry
@router.get("/complementry")
async def Room_Complementry(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                roomcomplementry_data = db.query(models.Room_Complementry).filter(models.Room_Complementry.status==CommonWords.STATUS).all()
                return templates.TemplateResponse('master_data/HOTEL/complementry.html', context={'request': request,'color_theme':color_theme,'roomcomplementry_data':roomcomplementry_data})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/add_complementry")
async def Add_Complementry(request: Request,db: Session = Depends(get_db),complementry_name:str=Form(...),complementry_description:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.Room_Complementry).filter(models.Room_Complementry.Complementry_Name == complementry_name,models.Room_Complementry.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    new_task_type = models.Room_Complementry(Complementry_Name=complementry_name,Description=complementry_description,status=CommonWords.STATUS,created_by=created_by,company_id=company_id)
                    db.add(new_task_type)
                    db.commit()
                    db.refresh(new_task_type)
                    
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.get("/get_complementry_id/{id}")
async def Get_Complementry_Id(request: Request,id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                complementry_data = db.query(models.Room_Complementry).filter(models.Room_Complementry.id==id).filter(models.Room_Complementry.status==CommonWords.STATUS).first()
                return JSONResponse(content=jsonable_encoder(complementry_data),status_code=status.HTTP_200_OK)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.post("/update_complementry")
async def Update_Room_Complementry(request: Request,db: Session = Depends(get_db),edit_id:int=Form(...),edit_complementry_name:str=Form(...),edit_complementry_description:str=Form(...)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                check_previous_data = db.query(models.Room_Complementry).filter(models.Room_Complementry.id!=edit_id,models.Room_Complementry.Complementry_Name == edit_complementry_name).filter(models.Room_Complementry.status==CommonWords.STATUS).all()
                if not check_previous_data:
                    db.query(models.Room_Complementry).filter(models.Room_Complementry.id==edit_id).update({'Complementry_Name':edit_complementry_name,'Description':edit_complementry_description})
                    db.commit()
                    return JSONResponse(content=jsonable_encoder('Ok'),status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content=jsonable_encoder('Error'),status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@router.delete("/delete_complementry/{id}")
async def deleting_Room_Complementry(request: Request,id:int,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                db.query(models.Room_Complementry).filter(models.Room_Complementry.id==id).update({'status':CommonWords.UNSTATUS})
                db.commit()
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

#=====================================>>> Reservation Status
@router.get("/reservation_status")
async def Reservation_Status(request: Request,db: Session = Depends(get_db)):   
    if "sessid" in request.session:
        token = request.session["sessid"]
        try:
            payload = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=[BaseConfig.ALGORITHM] )
            created_by: str= payload.get("user_id")
            company_id: str= payload.get("company_id")
            if created_by is None:
                return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)   
            else:
                color_theme = db.query(models.Themes).filter(models.Themes.status==CommonWords.STATUS).first()
                statuscolor_results = db.query(models.Reservation_Status).filter(models.Reservation_Status.status==CommonWords.STATUS).all()
                return templates.TemplateResponse('master_data/HOTEL/reservation_status.html', context={'request': request,'color_theme':color_theme,'statuscolor_results':statuscolor_results})
        except JWTError:
            return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT) 
    else:
        return RedirectResponse(CommonWords.LOGINER_URL, status_code=status.HTTP_307_TEMPORARY_REDIRECT)