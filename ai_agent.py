from openai import AsyncOpenAI
import os
from prompts import SYSTEM_PROMPT

client = None

def init_openai():
    global client
    client = AsyncOpenAI(api_key=os.getenv("gpt_key"))

async def generate_reply(chat_history: list) -> str:
    if client is None:
        init_openai()
        
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + chat_history
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",  
            messages=messages,
            temperature=0.7, 
            max_tokens=250,  
        )
        reply = response.choices[0].message.content.strip()
        return reply
        
    except Exception:
        return "Connection error, please try again."
