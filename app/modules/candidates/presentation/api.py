from fastapi import APIRouter

router = APIRouter(prefix="/candidates", tags=["candidates".replace("_", " ").title()])

@router.get("/")
async def list_candidates():
    return {"message": "candidates module - coming soon"}

@router.get("/{item_id}")
async def get_candidates(item_id: str):
    return {"message": "candidates module - coming soon"}

@router.post("/")
async def create_candidates():
    return {"message": "candidates module - coming soon"}

@router.patch("/{item_id}")
async def update_candidates(item_id: str):
    return {"message": "candidates module - coming soon"}

@router.delete("/{item_id}")
async def delete_candidates(item_id: str):
    return {"message": "candidates module - coming soon"}
