# tldw_tube/database/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from core.config import settings

load_dotenv()  

# Construct the database URL.  We'll get the components from our settings.
DATABASE_URL = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

# Create the database engine.  `echo=True` enables query logging (useful for debugging).
engine = create_engine(DATABASE_URL, echo=True)

# Create a session factory.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
class Base(DeclarativeBase):
    pass

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
