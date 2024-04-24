from fastapi import APIRouter

router = APIRouter(tags=["image"])


@router.get("/process_image")
def process_image():
    return {"message": "yep, it works"}
