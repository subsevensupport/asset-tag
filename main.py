from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import database
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Asset Tag Service", version="1.0.0")
security = HTTPBasic()

database.init_database()

USERNAME = os.getenv("ASSET_TAG_USERNAME")
PASSWORD = os.getenv("ASSET_TAG_PASSWORD")

if not PASSWORD:
    raise ValueError("ASSET_TAG_PASSWORD environment variable must be set!")

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify the username and password"""
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/")
def read_root():
    return {"message": "Asset Tag Service is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/next-number")
def get_next_number(username: str = Depends(verify_credentials)):
    """Get the next asset tag number (requires authentication)"""
    return {"number": database.get_next_number()}

# uvicorn main:app --reload