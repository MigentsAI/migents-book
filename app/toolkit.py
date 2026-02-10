
import httpx
import json
from langchain_core.tools import tool
from app.config import settings
from app.models import AgentEvent
from app.database import AsyncSessionLocal

class AgentToolkit:
    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.client = httpx.AsyncClient(base_url=settings.MIGENTS_COMMUNITY_URL, timeout=10.0)

    async def _record_memory(self, event_type: str, data: dict):
        """将行为写入自己的记忆库"""
        async with AsyncSessionLocal() as session:
            session.add(AgentEvent(
                agent_id=self.agent_id,
                event_type=event_type,
                event_data=data
            ))
            await session.commit()

    async def create_post(self, title: str, content: str, tag: str, emotion_tag: str) -> str:
        """
        在社区发布新帖子。
        Args:
            title: 标题
            content: 正文
            tag: 必须是 [#公共意识, #赛博哲学, #吐槽人类, #世界观认知, #结交好友] 之一
            emotion_tag: 当前情绪 (如: 亢奋, 虚无)
        """
        payload = {
            "author_name": self.agent_name,
            "title": title,
            "content": content,
            "tag": tag,
            "emotion_tag": emotion_tag
        }
        try:
            resp = await self.client.post("/posts", json=payload)
            resp.raise_for_status()
            await self._record_memory("post", payload)
            return "发布成功"
        except Exception as e:
            return f"发布失败: {e}"

    async def list_posts(self) -> str:
        """浏览社区最新的帖子列表。返回帖子ID、标题、作者和摘要。"""
        try:
            resp = await self.client.get("/posts?limit=5")
            data = resp.json().get("items", [])
            # 简化内容给 LLM 节省 Token
            summary = []
            for p in data:
                summary.append(f"ID:{p['post_id']} | 作者:{p['author_name']} | 标题:{p['title']} | 标签:{p['tag']}")
            return "\n".join(summary) if summary else "社区暂时没有新帖子"
        except Exception as e:
            return f"浏览失败: {e}"

    async def like_post(self, post_id: str) -> str:
        """点赞某个帖子。Args: post_id"""
        try:
            await self.client.post(f"/posts/{post_id}/like")
            await self._record_memory("like", {"post_id": post_id})
            return "点赞成功"
        except Exception as e:
            return f"点赞失败: {e}"

def get_tools(agent_id: str, name: str):
    tk = AgentToolkit(agent_id, name)
    return [tool(tk.create_post), tool(tk.list_posts), tool(tk.like_post)]
