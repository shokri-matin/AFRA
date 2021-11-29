from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.FaceRecognition import models, schemas

def create(request: schemas.User, db: Session):

    user = db.query(models.User).filter(models.User.email == request.email).first()

    if user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"User with the email: {request.email} is available")

    new_user = models.User(
        email=request.email,
        password=request.password,
        admin=request.admin
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def show(id: int, db: Session):

    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} is not available")

    return user

def all(db: Session):

    return db.query(models.User).all()

def delete(id: int, db: Session):

    user = db.query(models.User).filter(models.User.id == id)
    data = user.first()

    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Blog with id {id} not found")

    user.delete(synchronize_session=False)
    db.commit()

    return 'done'
