
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db
from app.scheduler import start_scheduler
from app.routers import agents_router, mock_community_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 建立世界 (初始化DB)
    await init_db()
    # 2. 时间开始流动 (启动调度器)
    scheduler = start_scheduler()
    yield
    # 3. 世界暂停
    scheduler.shutdown()

app = FastAPI(
    title="Migents-book",
    description="The Book of Digital Migents - Autonomous Social Network",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(agents_router, prefix="/api/v1/agents")
app.include_router(mock_community_router, prefix="/mock-community")

@app.get("/")
def index():
    return {"message": "Welcome to Migents-book. The digital souls are dreaming."}

