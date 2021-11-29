import os
import uuid
import json
import shutil
from typing import List
from sqlalchemy.orm import Session
from fastapi import File, UploadFile, HTTPException, status

from app.FaceRecognition.face_model import FaceModel
from app.FaceRecognition import models

ROOT = os.path.join(os.path.abspath(os.curdir), 'Dataset')

async def create(name :str, files: List[UploadFile] = File(...), db: Session = None, userid = 1):

    fc = FaceModel(model='large', tolerance=.5, db=db)

    print(fc)

    dir = os.path.join(ROOT, name)

    if os.path.exists(dir):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                        detail=f"Dataset with name: {name} is available")
    else:
        os.mkdir(dir)

    try:
        for file in files:
            contents = await file.read() 
            id = uuid.uuid4()
            filename = str(id) + '.jpg'

            with open(os.path.join(dir, filename), "wb") as f:
                f.write(contents)

        
        for filename in os.listdir(dir):
            encoding = fc.feature_extraction(dir, filename)
            db.add(models.Dataset(
                        name,
                        json.dumps(encoding.tolist()),
                        userid
                        ))
        db.commit()
    except:
        db.rollback()
        os.rmdir(dir)
        return {'result': 'Database is not available please contact administrator'}
    

    return {'result': 'Dataset successfully published'}

async def delete(name: str, db: Session = None):

    dir = os.path.join(ROOT, name)

    if os.path.exists(dir):
        shutil.rmtree(dir, ignore_errors=True)

        data = db.query(models.Dataset).filter(models.Dataset.name == name)
        data.delete(synchronize_session=False)
        db.commit()

    else:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f"Dataset with name: {name} is not available")

def all(db: Session):
    data = db.query(models.Dataset.name).distinct()
    if not data:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                        detail=f"No data available")
    return list(data)