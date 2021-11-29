from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile, File
import uuid
import os


from app.FaceRecognition import models, schemas
from app.FaceRecognition.face_model import FaceModel


IMGROOT = os.path.join(os.path.abspath(os.curdir), 'Received', 'Image')
VIDROOT = os.path.join(os.path.abspath(os.curdir), 'Received', 'Video')

async def image_recognize(file: UploadFile = File(...), db: Session = None):
    fc = FaceModel(db=db)

    contents = await file.read() 
    id = uuid.uuid4()
    filename = str(id) + '.jpg'

    with open(os.path.join(IMGROOT, filename), "wb") as f:
        f.write(contents)

    return fc.image_recognition(IMGROOT, filename)

async def video_recognize(file: UploadFile = File(...), db: Session = None):

    fc = FaceModel(db = db)

    content = await file.read()
    id = uuid.uuid4()
    filename = str(id) + '.mp4'

    with open(os.path.join(VIDROOT, filename), 'wb') as f:
        f.write(content)

    return fc.video_recognition(VIDROOT, filename)
