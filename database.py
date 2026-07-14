from sqlmodel import SQLModel, create_engine, Session
from models import Task

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# echo=True prints out raw SQL statements to your console (super handy for debugging!)
engine = create_engine(sqlite_url, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

