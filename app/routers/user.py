from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from .. import models, schemas, utils, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post("/", 
          status_code=status.HTTP_201_CREATED, 
          response_model = schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    #hash the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password


    user_to_create=models.User(
        **user.dict()
    )
     
    db.add(user_to_create)
    db.commit()
    db.refresh(user_to_create)
    return user_to_create

@router.get("/",
         response_model=schemas.UserPersonalInfo)
def get_user_information(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    user_information = db.query(models.User).filter(models.User.id == current_user.id).first()

    if user_information is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = ("User with id: {%d} not found." % (id)))
     
    return user_information

@router.get("/{id}",
         response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    
    user_to_get = db.query(models.User).filter(models.User.id == id).first()

    if user_to_get is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = ("User with id: {%d} not found." % (id)))
     
    return user_to_get

@router.put("/password")
def change_password(user_check: schemas.UserCheckPassword, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    user_query = db.query(models.User).filter(models.User.id == current_user.id)
    user = user_query.first()

    print(user.password)

    if not utils.verify(user_check.old_password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=("Wrong password!"))

    user.password = utils.hash(user_check.password)
    
    user_query.update({models.User.password: user.password}, synchronize_session=False)
    db.commit()

    return ({"message": "Password changed!"})



