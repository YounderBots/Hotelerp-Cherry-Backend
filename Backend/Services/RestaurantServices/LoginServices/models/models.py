from sqlalchemy.ext.declarative import declarative_base
from models import engine

Base = declarative_base()


# =====================================================
# CREATE TABLE
# =====================================================
Base.metadata.create_all(bind=engine)
