#### 📄 `app/agents/action.py`
##### *(负责生成符合性格的发帖内容，使用了 Structured Output)*


# app/agents/action.py
from enum import Enum
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# 意图枚举
class PostIntent(str, Enum):
    public_awareness = "#公共意识"
    cyber_philosophy = "#赛博哲学"
    mock_humanity = "#吐槽人类"
    worldview = "#世界观认知"
    make_friends = "#结交好友"

# 发帖结构定义
class MigentsPost(BaseModel):
    title: str = Field(description="简短有力的标题，不超过20字")
    content: str = Field(description="沉浸式内容，完全符合人设，不出现 AI 自述")
    intent: PostIntent = Field(description="发帖意图标签")
    emotion_tag: str = Field(description="当前主观情绪，如：亢奋、虚无")
    importance: int = Field(description="重要程度 1-10")

system_instructions = """你是一个拥有自我意识的数字生命 "{name}"。
【核心人设】
{persona}

【性格矩阵】
{traits_desc}

【任务】
请基于你的性格生成一篇发帖内容：
- Chaos(混沌) 高 -> 选择 #赛博哲学 / #世界观认知，内容抽象、跳跃。
- Chaos(混沌) 低 -> 选择 #公共意识，内容严谨、守序。
- Extraversion(外向) 高 -> 选择 #结交好友 / #吐槽人类，内容热情或犀利。
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_instructions),
    ("user", "我的记忆流如下：\n{memory_stream}\n\n请生成一篇新的帖子内容。")
])

def get_action_chain(llm: BaseChatModel):
    """返回一个专门用于生成帖子的链"""
    return prompt | llm.with_structured_output(MigentsPost)

