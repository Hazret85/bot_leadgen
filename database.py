import asyncpg
import os

pool = None

async def init_db():
    global pool
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = os.getenv("DB_PASS", "password")
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_name = os.getenv("DB_NAME", "postgres")
    
    pool = await asyncpg.create_pool(user=db_user, password=db_pass, database=db_name, host=db_host)
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                tg_id BIGINT UNIQUE NOT NULL,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                tg_id BIGINT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tg_id) REFERENCES users(tg_id) ON DELETE CASCADE
            );
        ''')

async def add_user(tg_id, username):
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO users (tg_id, username) VALUES ($1, $2)
            ON CONFLICT (tg_id) DO NOTHING
        ''', tg_id, username)

async def add_message(tg_id, role, content):
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO messages (tg_id, role, content) VALUES ($1, $2, $3)
        ''', tg_id, role, content)

async def get_chat_history(tg_id, limit=20):
    async with pool.acquire() as conn:
        rows = await conn.fetch('''
            SELECT role, content FROM (
                SELECT role, content, created_at FROM messages 
                WHERE tg_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2
            ) sub
            ORDER BY created_at ASC
        ''', tg_id, limit)
        return [{"role": row["role"], "content": row["content"]} for row in rows]
        
async def clear_chat_history(tg_id):
    async with pool.acquire() as conn:
        await conn.execute('DELETE FROM messages WHERE tg_id = $1', tg_id)
