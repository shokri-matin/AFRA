from fastapi import FastAPI
from app.FaceRecognition import models
from app.FaceRecognition.database import engine
from app.FaceRecognition.routers import user, dataset, recognition
import uvicorn

app = FastAPI(
    title="AFRA [Automatic Face Recognition API]",
    version="0.1.0",
    description= "I Expose REST APIs to Help You to Recognize Faces In Images and Videos"
)

# if databse dose not exist, it will be created
models.Base.metadata.create_all(engine)

app.include_router(user.router)
app.include_router(dataset.router)
app.include_router(recognition.router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)