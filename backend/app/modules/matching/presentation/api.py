from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_matching():
    return {"message": "matching module - coming soon"}
