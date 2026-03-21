import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

env_db_path = os.getenv("CALLS_DB_PATH")
if env_db_path:
    db_path = Path(env_db_path)
elif os.name != "nt" and Path("/home").is_dir():
    # Azure App Service persists /home across restarts
    db_path = Path("/home/calls.db")
else:
    db_path = Path("./calls.db")

DATABASE_URL = f"sqlite:///{db_path.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
