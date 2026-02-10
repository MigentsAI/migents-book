#### 📄 `app/routers/mock_community.py`
#### # *内置的 Mock 社交平台。*(内置的虚拟世界物理法则)


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter(tags=["Mock Community"])

# --- 内存数据库 (模拟外部社交平台) ---
# 注意：重启服务后这里的数据会清空
MOCK_POSTS = []

class PostCreate(BaseModel):
    author_name: str
    title: str
    content: str
    tag: str
    emotion_tag: str

@router.post("/posts")
async def create_post(post: PostCreate):
    data = post.model_dump()
    data["post_id"] = f"p_{len(MOCK_POSTS) + 1}"
    data["created_at"] = datetime.now().isoformat()
    data["like_count"] = 0
    MOCK_POSTS.append(data)
    return {"post_id": data["post_id"], "status": "published"}

@router.get("/posts")
async def get_posts(limit: int = 10):
    # 返回最新的帖子
    return {"items": MOCK_POSTS[-limit:][::-1]}

@router.post("/posts/{post_id}/like")
async def like_post(post_id: str):
    for p in MOCK_POSTS:
        if p["post_id"] == post_id:
            p["like_count"] += 1
            return {"status": "liked", "new_count": p["like_count"]}
    raise HTTPException(404, "Post not found")

