from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_companies():
    return {"message": "companies module - coming soon"}
