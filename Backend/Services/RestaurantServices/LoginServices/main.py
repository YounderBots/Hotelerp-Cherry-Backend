from fastapi import FastAPI,status
from fastapi.middleware.cors import CORSMiddleware
from routes import router

from fastapi.responses import RedirectResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates 
from starlette.middleware.sessions import SessionMiddleware
app = FastAPI(title="HotelERP",version="1.00")

app.add_middleware(

    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key="some-random-string")
app.mount("/templates/static", StaticFiles(directory="templates/static"), name="static")
# GET operation at route '/'
@app.get('/')
def root_api():
    return RedirectResponse('../login', status_code=status.HTTP_307_TEMPORARY_REDIRECT)  

app.include_router(router, prefix='')