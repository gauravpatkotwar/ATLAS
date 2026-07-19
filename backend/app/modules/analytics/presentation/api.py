from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_analytics():
    return {"message": "analytics module - coming soon"}
