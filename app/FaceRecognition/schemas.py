from pydantic import BaseModel

# Request Schemas
class User(BaseModel):
    email: str
    password: str
    admin: bool

# Response Schemas
class ShowUser(BaseModel):
    email: str = None
    admin: bool = None
    
    class Config():
        orm_mode = True

class ShowDataset(BaseModel):
    name: str = None

    class Config():
        orm_mode = True