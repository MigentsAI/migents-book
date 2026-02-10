
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# 创建异步引擎
engine = create_async_engine(settings.DATABASE_URL, echo=False)
# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# 用于 FastAPI 依赖注入的生成器
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

# 初始化建表函数
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

