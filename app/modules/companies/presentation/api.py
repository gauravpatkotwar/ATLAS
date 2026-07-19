from fastapi import APIRouter

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("/")
async def list_companies():
    return {"message": "Companies module - coming soon"}

@router.get("/{company_id}")
async def get_company(company_id: str):
    return {"message": "Companies module - coming soon"}

@router.post("/")
async def create_company():
    return {"message": "Companies module - coming soon"}

@router.patch("/{company_id}")
async def update_company(company_id: str):
    return {"message": "Companies module - coming soon"}

@router.delete("/{company_id}")
async def delete_company(company_id: str):
    return {"message": "Companies module - coming soon"}