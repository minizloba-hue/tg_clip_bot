import aiosqlite
import asyncio

async def init():
    async with aiosqlite.connect("clips.db") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS clips (
            code TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            banner TEXT NOT NULL,
            ref_link TEXT NOT NULL
        )
        """)
        await db.commit()

asyncio.run(init())
print("База данных создана!")
