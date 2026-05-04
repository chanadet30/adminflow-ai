from sqlalchemy import Column, Integer, String, Boolean
from database import Base

# -------------------------
# USER
# -------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    premium = Column(Boolean, default=False)


# -------------------------
# EMAIL ANALYSÉ
# -------------------------

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)
    content = Column(String)
    result = Column(String)