import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.llm_service import llm_service

async def main():
    result = await llm_service.generate_response(user_id="test_user", session_id="test_session", query="How do I restart my internet router please")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
