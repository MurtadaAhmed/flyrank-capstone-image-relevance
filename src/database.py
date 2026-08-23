import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ImageRecord(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    subject = Column(String)
    caption = Column(String)
    metadata_tags = Column(JSON)
    confidence = Column(Float)
    embedding = Column(JSON)

class PostRecord(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    post_id_string = Column(String, unique=True, index=True)
    title = Column(String)
    content = Column(String)

class ReviewRecord(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    image_id = Column(Integer, ForeignKey("images.id"))
    is_approved = Column(Boolean)
    reason = Column(String)

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    init_db()