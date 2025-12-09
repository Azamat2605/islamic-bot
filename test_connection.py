import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def test():
    try:
        conn = await asyncpg.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", 6432)),
            user=os.getenv("DB_USER", "tgbot"),
            password=os.getenv("DB_PASS", ""),
            database=os.getenv("DB_NAME", "bot_db"),
        )
        print("Connection successful")
        await conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

asyncio.run(test())
