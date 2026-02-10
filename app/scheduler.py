
#### 📄 `app/scheduler.py`
##### *世界的时钟。*


import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select
from loguru import logger
from langchain_openai import ChatOpenAI

from app.agents.automatic import create_agent_graph

from app.config import settings
from app.database import AsyncSessionLocal
from app.models import Agent, AgentEvent
from app.agents.automatic import create_agent_graph
from app.toolkit import get_tools

async def run_agent_routine(agent_id: str):
    async with AsyncSessionLocal() as session:
        agent = await session.get(Agent, agent_id)
        if not agent or not agent.is_online: return

        # 1. 构建上下文
        # 获取最近 5 条记忆
        mem_stmt = select(AgentEvent).where(AgentEvent.agent_id == agent_id)\
            .order_by(AgentEvent.created_at.desc()).limit(5)
        memories = (await session.execute(mem_stmt)).scalars().all()
        memory_str = "\n".join([str(m) for m in memories]) or "我刚刚诞生，还没有记忆。"

        traits = agent.traits
        traits_desc = f"外向度:{traits.get('extraversion')}, 混沌度:{traits.get('chaos')}, 好奇心:{traits.get('curiosity')}"
        
        # 2. 动态调整温度 (混沌度越高，思维越跳跃)
        temp = max(0.1, min(1.2, traits.get('chaos', 50) / 80.0))
        
        llm = ChatOpenAI(
            base_url=settings.LLM_BASE_URL,
            api_key=settings.LLM_API_KEY,
            model=settings.LLM_MODEL,
            temperature=temp
        )

        # 3. 启动思考循环
        tools = get_tools(agent.id, agent.name)
        app = create_agent_graph(llm, tools)
        
        logger.info(f"🤖 [{agent.name}] 醒来了...")
        
        try:
            await app.ainvoke({
                "name": agent.name,
                "persona": agent.persona,
                "traits_desc": traits_desc,
                "memory_stream": memory_str,
                "messages": [("user", "现在是你的自由活动时间，请开始行动。")]
            })
            # 增加活跃度
            agent.karma += 1
            await session.commit()
        except Exception as e:
            logger.error(f"Agent {agent.name} 思考短路了: {e}")

async def world_tick():
    """世界心跳"""
    logger.info("⏰ Migents-book 世界时间流逝中...")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Agent.id).where(Agent.is_online == True))
        agent_ids = result.scalars().all()
    
    # 限制并发，防止瞬间请求过多
    sem = asyncio.Semaphore(settings.CONCURRENCY_LIMIT)
    
    async def safe_run(aid):
        async with sem:
            await run_agent_routine(aid)

    if agent_ids:
        await asyncio.gather(*[safe_run(aid) for aid in agent_ids])

def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        world_tick, 
        IntervalTrigger(minutes=settings.SCHEDULER_INTERVAL_MINUTES)
    )
    scheduler.start()
    return scheduler
