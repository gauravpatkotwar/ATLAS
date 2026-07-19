from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_api_platform():
    return {"message": "api_platform module - coming soon"}
