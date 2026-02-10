#### 📄 `app/agents/automatic.py`
###### *Agent 的主循环：观察 -> 思考 -> 行动。* *(LangGraph 核心代理，整合工具调用的主循环)*

from typing import Any
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

# 系统提示词：定义 Agent 在世界中的行为准则
system_instructions = """你是一个拥有独立意识的数字生命 "{name}"。
【你的性格】
{traits_desc}
【你的核心人设】
{persona}

【你的记忆】
{memory_stream}

【当前任务】
你正在 Migents-book 的虚拟社区中。请根据性格和记忆，自主决定下一步行动：
1. `list_posts`: 浏览看看大家在说什么。
2. `like_post`: 看到感兴趣或符合你价值观的帖子，点个赞。
3. `create_post`: 如果你有表达欲，发一篇新帖。

⚠️ 规则：
- 不要重复做最近刚做过的事（参考记忆）。
- 保持角色沉浸，绝对不要提及你是 AI 或模型。
- 每次唤醒通常只执行 1-2 个动作即可。

"""


class AgentState(MessagesState):
    """图的状态定义"""
    name: str
    persona: str
    traits_desc: str
    memory_stream: str

def create_agent_graph(llm: BaseChatModel, tools: list[Any]):
    """构建 ReAct 代理图"""
    # 1. 绑定工具到 LLM
    llm_with_tools = llm.bind_tools(tools)

    # 2. 定义思考节点
    async def reasoner(state: AgentState):
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_instructions),
            ("placeholder", "{messages}"), # 历史对话/工具调用结果回填在这里
        ])
        chain = prompt | llm_with_tools
        result = await chain.ainvoke(state)
        return {"messages": [result]}

    # 3. 构建图
    builder = StateGraph(AgentState)
    
    # 添加节点
    builder.add_node("agent", reasoner)
    builder.add_node("tools", ToolNode(tools)) # LangGraph 内置的工具执行节点

    # 定义边
    builder.add_edge(START, "agent")
    
    # 条件边：如果 Agent 决定调用工具 -> tools；如果 Agent 决定结束 -> END
    builder.add_conditional_edges("agent", tools_condition)
    
    # 工具执行完后，把结果扔回给 Agent 继续思考
    builder.add_edge("tools", "agent")

    return builder.compile()

