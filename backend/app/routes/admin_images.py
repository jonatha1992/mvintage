from typing import Literal

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import require_manager_or_admin


router = APIRouter(
    prefix="/admin/images",
    tags=["admin"],
    dependencies=[Depends(require_manager_or_admin())],
)


class ImageUploadResponse(BaseModel):
    secure_url: str


@router.post("/upload", response_model=ImageUploadResponse)
def upload_image(
    file: UploadFile = File(...),
    folder: Literal["productos", "productos/originals"] = Form(...),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=422, detail="El archivo debe ser una imagen")
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > 15 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="La imagen supera el límite de 15 MB")
    if not settings.IMG_SERVER_API_KEY:
        raise HTTPException(status_code=503, detail="Servidor de imágenes no configurado")
    try:
        with httpx.Client(timeout=60) as client:
            response = client.post(
                f"{settings.IMG_SERVER_URL.rstrip('/')}/v1/showroomisabella/upload",
                headers={"X-API-Key": settings.IMG_SERVER_API_KEY},
                data={"folder": folder},
                files={"file": (file.filename, file.file, file.content_type)},
            )
        response.raise_for_status()
        data = response.json()
        url = data.get("secure_url")
        if not isinstance(url, str) or not url.startswith("https://"):
            raise ValueError("URL inválida")
    except (httpx.HTTPError, ValueError, AttributeError) as exc:
        raise HTTPException(status_code=502, detail="Error del servidor de imágenes") from exc
    return ImageUploadResponse(secure_url=url)
