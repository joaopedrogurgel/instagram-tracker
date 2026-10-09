from fastapi import APIRouter

router = APIRouter()


@router.get("/saude")
async def saude() -> dict[str, str]:
    return {"status": "ok"}
