from fastapi import FastAPI
import database

app = FastAPI(title="Asset Tag Service", version="1.0.0")

database.init_database()

@app.get("/")
def read_root():
    return {"message": "Asset Tag Service is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/next-number")
def get_next_number():
    return {"number": database.get_next_number()}