from sqlalchemy import Column, Integer, String, JSON, create_engine, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from infrastructure import Config

Base = declarative_base()


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String, unique=True, nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    whitelist = Column(String)


class Database:
    def __init__(self):
        self.config = Config()
        self.db_url = self.config.DB_URL
        self.engine = create_engine(self.db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.create_tables()

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()
