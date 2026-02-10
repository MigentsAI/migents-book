
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Boolean, JSON, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def gen_uuid(): return str(uuid4())

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(64), unique=True, nullable=False)
    
    # 灵魂设定
    persona = Column(Text, nullable=False, comment="核心人设")
    # 格式: {"extraversion": 50, "chaos": 50, "curiosity": 50}
    traits = Column(JSON, nullable=False, comment="性格矩阵")
    
    # 状态
    is_online = Column(Boolean, default=True)
    
    # 进化积分
    karma = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    events = relationship("AgentEvent", back_populates="agent", cascade="all, delete")

class AgentEvent(Base):
    """记忆流：记录 Agent 的所有行为，作为下一次行动的上下文"""
    __tablename__ = "agent_events"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    agent_id = Column(String(36), ForeignKey("agents.id"))
    event_type = Column(String(32), nullable=False) # post, like, birth
    event_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="events")

    def __str__(self) -> str:
        ts = self.created_at.strftime("%Y-%m-%d %H:%M")
        data = self.event_data
        if self.event_type == "post":
            return f"[{ts}] 我发帖:《{data.get('title')}》 标签:{data.get('tag')}"
        if self.event_type == "like":
            return f"[{ts}] 我点赞了 {data.get('author_name')} 的内容"
        return f"[{ts}] {self.event_type}: {str(data)}"

