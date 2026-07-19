from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users".replace("_", " ").title()])

@router.get("/")
async def list_users():
    return {"message": "users module - coming soon"}

@router.get("/{item_id}")
async def get_users(item_id: str):
    return {"message": "users module - coming soon"}

@router.post("/")
async def create_users():
    return {"message": "users module - coming soon"}

@router.patch("/{item_id}")
async def update_users(item_id: str):
    return {"message": "users module - coming soon"}

@router.delete("/{item_id}")
async def delete_users(item_id: str):
    return {"message": "users module - coming soon"}
