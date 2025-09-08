from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_v2():
    # 与 v1 区分一下返回内容
    return {"status": "ok", "version": 2}