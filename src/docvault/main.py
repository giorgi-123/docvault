from fastapi import FastAPI, HTTPException

from docvault.routers.auth import router
from docvault.routers.folder import folder_router


app = FastAPI(
    title="Document Vault",
    description="A place where you can save your documents using API endpoints",
    version="0.1.0"
)

@app.get("/health")
def health_check():
    """
        Health check endpoint
    """
    return {"status": "healthy"}


app.include_router(router)
app.include_router(folder_router)