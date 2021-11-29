from starlette import status
from typing import List
from sqlalchemy.orm.session import Session
from fastapi import APIRouter, File, UploadFile, Depends

from app.FaceRecognition.repository import dataset
from app.FaceRecognition import database, schemas

get_db = database.get_db

router = APIRouter(
    prefix="/dataset",
    tags=['Dataset']
)

@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create(name :str, files: List[UploadFile] = File(...), db: Session = Depends(get_db), userid=1):
    return await dataset.create(name, files, db, userid)


@router.get('/all', response_model=List[schemas.ShowDataset])
def all(db: Session = Depends(get_db)):
    return dataset.all(db)


@router.delete('/delete/{name}', status_code=status.HTTP_204_NO_CONTENT)
async def delete(name: str, db: Session = Depends(get_db)):
    print('router')
    return await dataset.delete(name, db)