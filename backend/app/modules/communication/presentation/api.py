from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_communication():
    return {"message": "communication module - coming soon"}
