from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# tells sqlalchemy where to connect - in our case that's sqlite
# ./blog.db is current directory, and blog.db will be automatically created
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

# check_same_thread is something about concurrency (?) and its False setting 
# is specifically for sqlite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# session is a contract with database; each request to the database is a session
# all the falses are standard patterns with fastapi; we want to control when changes are stored
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# 'a dependency function that provides sessions to our routes' 
# i don't know what this means
# "hey this route needs a dependency session to work, so give it one"
def get_db():
    with SessionLocal() as db:
        yield db
    # crucially this cleans up a database session after each request finishes
    # one session per request
    # clean; standard fastapi pattern