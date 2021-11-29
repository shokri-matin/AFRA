from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm.session import Session
from starlette import status

from app.FaceRecognition import database, schemas
from app.FaceRecognition.repository import user

router = APIRouter(
    prefix="/user",
    tags=['Users']
)

get_db = database.get_db

@router.post('/create', response_model=schemas.ShowUser, status_code=status.HTTP_201_CREATED)
def create(request: schemas.User, db: Session = Depends(get_db)):
    return user.create(request, db)

@router.get('/show/{id}', response_model=schemas.ShowUser)
def show(id: int, db: Session = Depends(get_db)):
    return user.show(id, db)

@router.get('/all', response_model=List[schemas.ShowUser])
def all(db: Session = Depends(get_db)):
    return user.all(db)

@router.delete('/delete/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete(id, db: Session = Depends(get_db)):
    return user.delete(id, db)