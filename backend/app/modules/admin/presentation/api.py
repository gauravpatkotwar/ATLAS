from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_admin():
    return {"message": "admin module - coming soon"}
