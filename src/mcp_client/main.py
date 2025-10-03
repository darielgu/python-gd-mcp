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

        files = result.get("files", []) if isinstance(result, dict) else []
        if files:
            print("Matched files:")
            for entry in files:
                name = entry.get("name", "<unknown>")
                file_id = entry.get("id", "<missing>")
                mime = entry.get("mime_type", "<unknown>")
                print(f"  • {name} ({mime}) id={file_id}")
        else:
            error = result.get("error") if isinstance(result, dict) else None
            print("No files found." if not error else f"Search error: {error}")

        output = await client.call_tool(
            "gdrive_read_file",
            {"file_id": "1C37Gzd5IQs8E3BmTWRbqUrX2b1Y6tT-EjEJdahpuldg", "user_id": USERID}
        )

        if isinstance(output, dict):
            metadata = output.get("metadata", {})
            name = metadata.get("name", "<unknown>")
            link = metadata.get("webViewLink")
            print(f"\nFile: {name}")
            if link:
                print(f"Link: {link}")

            content = output.get("content")
            if isinstance(content, str):
                preview = content.strip().replace("\n", " ")
                if len(preview) > 200:
                    preview = preview[:200] + "…"
                print(f"Content preview: {preview}")
            else:
                print("No text content available.")
        else:
            print("Failed to read file.")

# def main() -> None:



if __name__ == "__main__":
    asyncio.run(main())
