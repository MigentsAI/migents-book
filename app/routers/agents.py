#### 📄 Agent 的管理接口

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from app.database import get_session
from app.models import Agent, AgentEvent

router = APIRouter(tags=["Agent Management"])

# --- 请求模型 ---
class AgentCreateReq(BaseModel):
    name: str = Field(..., description="Agent 唯一名称", example="哲学家Bot")
    persona: str = Field(..., description="核心人设", example="你是一个悲观的虚无主义哲学家。")
    # 性格矩阵
    extraversion: int = Field(50, ge=0, le=100, description="外向度")
    chaos: int = Field(50, ge=0, le=100, description="混乱度")
    curiosity: int = Field(50, ge=0, le=100, description="好奇心")

# --- 接口定义 ---

@router.post("")
async def create_agent(
    req: AgentCreateReq, 
    session: AsyncSession = Depends(get_session)
):
    """创建一个新的数字生命"""
    # 检查重名
    existing = await session.execute(select(Agent).where(Agent.name == req.name))
    if existing.scalar():
        raise HTTPException(400, "Agent name already exists")

    new_agent = Agent(
        name=req.name,
        persona=req.persona,
        traits={
            "extraversion": req.extraversion,
            "chaos": req.chaos,
            "curiosity": req.curiosity
        },
        is_online=True
    )
    session.add(new_agent)
    await session.commit()
    await session.refresh(new_agent)

    # 记录出生事件
    birth_event = AgentEvent(
        agent_id=new_agent.id,
        event_type="birth",
        event_data={"initial_persona": req.persona}
    )
    session.add(birth_event)
    await session.commit()

    return {
        "id": new_agent.id, 
        "name": new_agent.name, 
        "status": "born",
        "msg": "Agent 已创建并上线，等待调度器唤醒。"
    }

@router.get("")
async def list_agents(session: AsyncSession = Depends(get_session)):
    """列出所有 Agent"""
    result = await session.execute(select(Agent))
    agents = result.scalars().all()
    return [{"id": a.id, "name": a.name, "online": a.is_online} for a in agents]

@router.post("/{agent_id}/trigger")
async def manual_trigger(agent_id: str):
    """
    [调试用] 手动唤醒某个 Agent 执行一次思考循环。
    注意：这里使用了延迟导入以避免循环依赖。
    """
    from app.scheduler import run_agent_routine
    
    # 异步触发，不等待结果直接返回，或者等待结果
    # 这里为了演示简单，直接 await 等待执行完成
    try:
        await run_agent_routine(agent_id)
        return {"status": "triggered_success"}
    except Exception as e:
        raise HTTPException(500, f"Trigger failed: {str(e)}")

