"""定时任务调度器 - 用于发布定时文章等后台任务。"""

import asyncio
from datetime import datetime, timezone

from app.core.database import AsyncSessionLocal


async def check_scheduled_articles():
    """检查并发布到期的定时文章。"""
    try:
        from app.services.article import publish_scheduled_articles
        
        async with AsyncSessionLocal() as session:
            published_count = await publish_scheduled_articles(session)
            if published_count > 0:
                print(f"[{datetime.now(timezone.utc).isoformat()}] 已自动发布 {published_count} 篇定时文章")
    except Exception as e:
        print(f"[{datetime.now(timezone.utc).isoformat()}] 发布定时文章时出错: {e}")


async def scheduler_loop():
    """调度器主循环，每 60 秒检查一次定时文章。"""
    while True:
        await check_scheduled_articles()
        await asyncio.sleep(60)


def start_scheduler():
    """启动调度器（在应用启动时调用）。"""
    import threading
    
    def run_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(scheduler_loop())
    
    thread = threading.Thread(target=run_loop, daemon=True, name="article-scheduler")
    thread.start()
    print("定时文章调度器已启动")
