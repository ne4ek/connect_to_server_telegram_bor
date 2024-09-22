from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Tg_user(Base):
    __tablename__ = 'tg_users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    first_name= Column(String )
    last_name = Column(String, nullable=True)
    username = Column(String)
    
    hosts = relationship("Host", back_populates="user")

class Host(Base):
    __tablename__ = 'hosts'
    
    id = Column(Integer, primary_key=True)
    label = Column(String)
    host_name = Column(String)
    user_name = Column(String)
    password = Column(String)
    tg_user_id = Column(Integer, ForeignKey('tg_users.id'))
    
    user = relationship("Tg_user", back_populates="hosts")
    
    def __str__(self):
        return f"Host(label='{self.label}', host_name='{self.host_name}', user_name='{self.user_name}')"

    def __repr__(self):
        return f"<Host(id={self.id}, label='{self.label}', host_name='{self.host_name}', user_name='{self.user_name}', tg_user_id={self.tg_user_id})>"
    
    
DATABASE_URL = "sqlite:///./test.db"  

engine = create_engine(DATABASE_URL, echo=True, isolation_level="AUTOCOMMIT")
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

# Create all tables
def init_db():
    Base.metadata.create_all(bind=engine)
