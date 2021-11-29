import re
from sqlalchemy import Column, JSON, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, validates

from app.FaceRecognition.database import Base

class Dataset(Base):

    __tablename__ = "dataset"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120))
    feature = Column(JSON)

    user_id = Column(Integer, ForeignKey('users.id'))

    creator = relationship("User", back_populates="data")

    def __init__(self, name, feature, user_id):
        self.name = name
        self.feature = feature
        self.user_id = user_id

    def __repr__(self):
        return f'{self.name}, {self.user_id}'

class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), nullable=False)
    password = Column(String(120), nullable=False)
    admin = Column(Boolean, default=False)

    data = relationship("Dataset", back_populates="creator")

    def __init__(self, email, password, admin) -> None:
        self.email = email
        self.password = password
        self.admin = admin

    def __repr__(self) -> str:
        return f'User: {self.email}, Is Admin: {self.admin}'

    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise AssertionError('No email provided')

        if not re.match("[^@]+@[^@]+\.[^@]+", email):
            raise AssertionError('Provided email is not an email address') 

        return email

    @validates('password')
    def validate_password(self, key, password):
        if not password:
            raise AssertionError('No Password Provided')
        
        if len(password) < 5:
            raise AssertionError('Password length must be greater than 5')

        return password