from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import config

Base = declarative_base()

engine = create_engine(config.DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, future=True)


def init_db():
    import db.models  # noqa: F401  ensure models are registered
    Base.metadata.create_all(bind=engine)
