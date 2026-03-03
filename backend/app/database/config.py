from sqlmodel  import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL não configurada.")


engine = create_engine(DATABASE_URL, echo=False) 

# open and close session for each request
def get_db():   
    with Session(engine) as session:
        yield session

# Initialize the database 
def init_db():
    SQLModel.metadata.create_all(engine)
   