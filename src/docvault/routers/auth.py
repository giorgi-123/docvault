from fastapi import FastAPI
from docvault.schemas.user import UserCreate, UserLogin, UserResponse, Token


app = FastAPI(
    title="Doc Vault",
    description="Document vault",
    version="0.1.0")


@app.post("/auth/register", response_model=UserResponse)
def register(data: UserCreate):
    pass


@app.post("/auth/login", response_model=Token)
def login(data: UserLogin):
    pass
