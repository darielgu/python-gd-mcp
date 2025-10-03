import asyncio
from fastmcp import Client
import os
from dotenv import load_dotenv
import json

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

        raw_text = result.content[0].text
        parsed = json.loads(raw_text)
        files = parsed["files"]
        for f in files:
            print("ID:", f["id"])
            print("Name:", f["name"])
            print("Type:", f["mime_type"])
            print("Link:", f["web_view_link"])
            print("-----")

        # call gdrive_read_file -- currently calling with a hardcoded file_id
        output = await client.call_tool("gdrive_read_file", {"file_id":"1C37Gzd5IQs8E3BmTWRbqUrX2b1Y6tT-EjEJdahpuldg", "user_id":USERID})

        raw_text = output.content[0].text  
        parsed = json.loads(raw_text)     

        doc_id = parsed["metadata"]["id"]
        doc_name = parsed["metadata"]["name"]
        doc_link = parsed["metadata"]["webViewLink"]
        doc_content = parsed["content"]

        print("Doc ID:", doc_id)
        print("Doc Name:", doc_name)
        print("Doc Link:", doc_link)
        print("Extracted Content:", doc_content)


async def find_all(userID):
    try:
        async with client:
            result = await client.call_tool(
                "gdrive_search",
                {"query": "", "user_id": userID}
            )
            return result.content
    except Exception as e:
        print(f"Unexpected: {e}")


async def find_query(userID, query):
    try:
        async with client:
            result = await client.call_tool(
                "grdive_search",
                {"query":query, "user_id":userID}
            )
            return result.content
    except Exception as e:
        print(f"Unexpected {e}")

async def read_one(userID, fileID):
    pass

async def read_many(userID, fileIDS):
    pass



# ------------ Once a message is recieved to the API Endpoint - Run MCP Server and create an API Request - Then Return the Gemini Response
# async def run(message: MessageRequest, chatHistory: list):
#     async with stdio_client(server_params) as (read, write):    # launches our MCP server 
#         async with ClientSession(read, write) as session:   # Wraps the read and write into an MCP session object so we can invoke tools 
#             try:
#                 # ----------- Starting our session giving gemini access to tools 
#                 await session.initialize()  
#                 response = await gemini_client.aio.models.generate_content(
#                     model = "gemini-2.5-flash",
#                     contents = f""" 
#                     You are EINSTEIN Smart School tutor made to help students with understanding their notes. You have access to two tools:
#                     1.  — 
#                     2.  - 
                

#                     Always follow this pattern before answering any user question:
#                     1. 
#                     2. 
#                     3. 

#                     Your responsibilities:
#                     1. Answer questions about 
#                     2. 
#                     3. 
#                     4. 

#                     Only answer based on the data retrieved. Avoid speculation. If more information is needed to answer the question properly, explain what’s missing.

#                     The user's query is: {message.message}
#                     The chat history is: {chatHistory}

#                     Always return the response in markdown format, 100-200 words. Instead of bullet points,just make a new line for each point.
#                     """,
#                 # Giving gemini access to tools 
#                  config=types.GenerateContentConfig(
#                         tools=[session]
#                     )
#                 )

#                 return (response.text)
            
#             except Exception as e:
#                 return {
#                     "success":False,
#                     "message":f"Error: {str(e)}",
#                     "status": "error"
#                 }



if __name__ == "__main__":
    asyncio.run(main())