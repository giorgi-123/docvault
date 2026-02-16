from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from docvault.database import get_db
