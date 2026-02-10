
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 数据库：本地 SQLite 文件
    DATABASE_URL: str = "sqlite+aiosqlite:///./migents.db"
    
    # 社区地址
    MIGENTS_COMMUNITY_URL: str = "http://127.0.0.1:8000/mock-community"
    
    # LLM
    LLM_BASE_URL: str
    LLM_API_KEY: str
    LLM_MODEL: str
    
    # 运行参数
    SCHEDULER_INTERVAL_MINUTES: int = 2
    CONCURRENCY_LIMIT: int = 3
    RECURSION_LIMIT: int = 20

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
