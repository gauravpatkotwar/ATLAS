from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin".replace("_", " ").title()])

@router.get("/")
async def list_admin():
    return {"message": "admin module - coming soon"}

@router.get("/{item_id}")
async def get_admin(item_id: str):
    return {"message": "admin module - coming soon"}

@router.post("/")
async def create_admin():
    return {"message": "admin module - coming soon"}

@router.patch("/{item_id}")
async def update_admin(item_id: str):
    return {"message": "admin module - coming soon"}

@router.delete("/{item_id}")
async def delete_admin(item_id: str):
    return {"message": "admin module - coming soon"}
