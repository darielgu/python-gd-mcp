from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from fastapi.responses import RedirectResponse, JSONResponse

from src.auth.main import get_auth_url, handle_oauth_callback, get_google_email 


app = FastAPI()

@app.get("/")
def session():
    return ('app running')

@app.get("/signup") 
def signup():
    # Add logic for user Sign Up 

    # Generate Google OAuth URL
    auth_url, _ = get_auth_url()
    return RedirectResponse(auth_url)


@app.get("/auth/google/callback")
def auth_google_callback(code: str):
    
    creds = handle_oauth_callback(code)
    email = get_google_email(creds["access_token"])

    # add Logic Here where we update DB with matching that email to our signup email and append Tokens
    return JSONResponse({
        "message": "OAuth signup successful!",
        "access_token": creds["access_token"],
        "refresh_token": creds["refresh_token"],
        "expiry": creds["expiry"],
        "email":email
    })
    # return RedirectResponse('http://localhost:3000/dashboard')


if __name__ == "__main__":
    uvicorn.run("src.app.main:app", host="localhost", port=3000, log_level="info")