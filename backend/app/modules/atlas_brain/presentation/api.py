from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_atlas_brain():
    return {"message": "atlas_brain module - coming soon"}
