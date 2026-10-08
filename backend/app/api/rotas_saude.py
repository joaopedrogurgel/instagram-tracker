from fastapi import APIRouter

router = APIRouter()

@router.get("/saude")
async def saude():
    return {"status": "ok"}
