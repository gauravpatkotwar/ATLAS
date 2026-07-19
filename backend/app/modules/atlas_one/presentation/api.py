from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_atlas_one():
    return {"message": "atlas_one module - coming soon"}
