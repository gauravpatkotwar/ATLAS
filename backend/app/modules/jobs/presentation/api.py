from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_jobs():
    return {"message": "jobs module - coming soon"}
