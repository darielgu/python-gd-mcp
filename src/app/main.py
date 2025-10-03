from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

@app.get("/")
def session():
    return ('app running')



if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info")