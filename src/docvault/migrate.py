import asyncio
from sqlalchemy import text
from docvault.database import engine, Base

async def run_migrations():
    """Create all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # Verify tables were created
        result = await conn.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        ))
        tables = [row[0] for row in result.fetchall()]
        return tables


def handler(event, context):
    """Lambda handler to run migrations."""
    tables = asyncio.run(run_migrations())
    
    return {
        "statusCode": 200,
        "body": {
            "message": "Migrations complete",
            "tables": tables
        }
    }