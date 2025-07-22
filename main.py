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
READONLY_USERNAME = os.getenv("ASSET_TAG_READONLY_USERNAME")
READONLY_PASSWORD = os.getenv("ASSET_TAG_READONLY_PASSWORD")

if not PASSWORD:
    raise ValueError("ASSET_TAG_PASSWORD environment variable must be set!")

if not READONLY_PASSWORD:
    raise ValueError("ASSET_TAG_READONLY_PASSWORD environment variable must be set!")

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

def verify_readonly_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify the read-only username and password"""
    correct_username = secrets.compare_digest(credentials.username, READONLY_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, READONLY_PASSWORD)
    
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

@app.get("/peek-next-number")
def peek_next_number(username: str = Depends(verify_readonly_credentials)):
    """Check the next asset tag number without consuming it (read-only access)"""
    return {"number": database.peek_next_number()}
    
# uvicorn main:app --reload