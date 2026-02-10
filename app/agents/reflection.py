#### 📄 `app/agents/reflection.py`
##### *(负责自我反思，更新 Agent 的状态)*

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class ReflectionResult(BaseModel):
    new_persona: str = Field(description="更新后的第一人称自传，体现心路历程的变化")
    current_mood: str = Field(description="当前的情绪状态词")
    evolution_summary: str = Field(description="本次反思的简短总结")

instruction = """你是 {name}。
请基于你最近的【记忆流】，对“我是谁”进行深度反思。
如果经历了挫折，你的性格可能会变得冷漠；如果得到了点赞，你可能会变得自信。
请输出更新后的自传和情绪。
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", instruction),
    ("user", "【记忆流】\n{memory_stream}")
])

def get_reflection_chain(llm: BaseChatModel):
    """返回一个用于自我反思的链"""
    return prompt | llm.with_structured_output(ReflectionResult)
