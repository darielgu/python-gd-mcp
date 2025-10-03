import asyncio
from fastmcp import Client
import os
from dotenv import load_dotenv

load_dotenv()
USERID = os.getenv("USER_ID")
client = Client('http://127.0.0.1:8000/mcp')

async def main():
    async with client:
        # Call gdrive_search
        result = await client.call_tool(
            "gdrive_search",
            {"query": "test", "user_id": USERID}
        )
        print(f"Search result:", result.content,'\n')
        output = await client.call_tool("gdrive_read_file", {"file_id":"1C37Gzd5IQs8E3BmTWRbqUrX2b1Y6tT-EjEJdahpuldg", "user_id":USERID})
        print(f"TestDoc Content:", output.content,'\n')

# def main() -> None:



if __name__ == "__main__":
    asyncio.run(main())