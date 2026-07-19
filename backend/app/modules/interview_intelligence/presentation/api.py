from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_interview_intelligence():
    return {"message": "interview_intelligence module - coming soon"}
