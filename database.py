from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# tells sqlalchemy where to connect - in our case that's sqlite
# ./blog.db is current directory, and blog.db will be automatically created
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"

# check_same_thread is something about concurrency (?) and its False setting 
# is specifically for sqlite
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# session is a contract with database; each request to the database is a session
# all the falses are standard patterns with fastapi; we want to control when changes are stored
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False, # recommended for async; smth about preventing auto- lazy loading which doesnt work in async
)

class Base(DeclarativeBase):
    pass

# 'a dependency function that provides sessions to our routes' 
# i don't know what this means
# "hey this route needs a dependency session to work, so give it one"
async def get_db():
    async with AsyncSessionLocal() as session: # still yields db session, just async session now
        yield session
    # crucially this cleans up a database session after each request finishes
    # one session per request
    # clean; standard fastapi pattern