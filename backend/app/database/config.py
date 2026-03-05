from sqlmodel  import SQLModel, create_engine, Session
# Importação explícita dos models para registrar as tabelas
from app.models.collections import Collection
from app.models.domain import Domain
from app.models.user import User
import os
from dotenv import load_dotenv
from typing import Optional


from threading import Lock
from supabase import create_client, Client

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise ValueError("DATABASE_URL não configurada. Defina DATABASE_URL ")

if DATABASE_URL.startswith("postgres") and "sslmode=" not in DATABASE_URL:
    separator = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{separator}sslmode=require"

try:
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
except Exception as e:
    raise ValueError(f"Erro ao criar engine do banco de dados: {e}")


_supabase_client: Optional[Client] = None
_supabase_lock = Lock()




def get_supabase_client() -> Client:
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    with _supabase_lock:
        if _supabase_client is None:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")

            if not supabase_url or not supabase_key:
                raise ValueError(
                    "SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY são obrigatórios"
                )

            _supabase_client = create_client(supabase_url, supabase_key)

    return _supabase_client



# open and close session for each request
def get_db():   
    with Session(engine) as session:
        yield session

# Initialize the database 
def init_db():
    SQLModel.metadata.create_all(engine)
   