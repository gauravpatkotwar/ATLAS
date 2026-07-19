from fastapi import APIRouter

router = APIRouter(prefix="/matching", tags=["matching".replace("_", " ").title()])

@router.get("/")
async def list_matching():
    return {"message": "matching module - coming soon"}

@router.get("/{item_id}")
async def get_matching(item_id: str):
    return {"message": "matching module - coming soon"}

@router.post("/")
async def create_matching():
    return {"message": "matching module - coming soon"}

@router.patch("/{item_id}")
async def update_matching(item_id: str):
    return {"message": "matching module - coming soon"}

@router.delete("/{item_id}")
async def delete_matching(item_id: str):
    return {"message": "matching module - coming soon"}
