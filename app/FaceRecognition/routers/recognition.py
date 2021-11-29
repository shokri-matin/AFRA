from starlette import status
from typing import List
from sqlalchemy.orm.session import Session
from fastapi import APIRouter, File, UploadFile, Depends

from app.FaceRecognition.repository import recognition
from app.FaceRecognition import database, schemas

get_db = database.get_db

router = APIRouter(
    prefix="/recognition",
    tags=['Face Recognition']
)

@router.post('/image_recognition')
async def image_recognition(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await recognition.image_recognize(file, db)

@router.post('/video_recognition')
async def video_recognition(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await recognition.video_recognize(file, db)