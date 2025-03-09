from aiohttp import payload_type
from fastapi import APIRouter,Depends,HTTPException
from pydantic.v1 import BaseModel
from database import SessionLocal
from sqlalchemy.util import deprecated
from typing import Annotated
from sqlalchemy.orm import Session
from modals import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm,OAuth2AuthorizationCodeBearer
from starlette import status
from datetime import timedelta,datetime,timezone
from jose import jwt,JWTError
router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

SECRET_KEY="NpZtCOh2HaaLaodrBceFCXfU8QP9HMuQ"  #anahtar kelimemiz
ALGORITHM="HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dbDep = Annotated[Session, Depends(get_db)]


bcrypt_context=CryptContext(schemes=["bcrypt"],deprecated="auto")
oauth2_bearer=OAuth2AuthorizationCodeBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    username=str,
    email = str,
    firstname=str,
    lastname=str,
    password=str,
    role=str

class Token(BaseModel):
    access_token=str,
    token_type:str

def authenticate_user(username:str,password:str,db):
    user=db.query(Users).filter(username==username).first()


@router.post("/")
async def create_user(db:dbDep ,create_user_request:CreateUserRequest):
    user=Users(
        username=create_user_request.username,
        email=create_user_request.email,
        firstname=create_user_request.firstname,
        lastname=create_user_request.lastname,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
        is_active=True
    )
    dbDep.add(user)
    dbDep.commit()
async def create_token(username:str,user_id:int,role:str,expire_delta:timedelta):

    payload={'sub':username,'id':user_id,'role':role}
    #ne zaman geçerliliği kaybedecek
    expires=datetime.now(timezone.utc)+expire_delta
    payload.update({'exp':expires})
    return jwt.encode(payload_type,SECRET_KEY,algorithm=ALGORITHM)

def authenticate_user(username:str,password:str,db):
    user=db.query(Users).filter(Users.username==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user

async def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username=payload.get('sub')
        user_id=payload.get('id')
        user_role=payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return{'username':username,'id':user_id,'user_role':user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)





@router.post("/token",response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()] ,
                                 db:dbDep):
    user=authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    token=create_token(user.username,user.id,user.role,timedelta(minutes=60))
    return {"acces_token":token,"token_type":"bearer"}