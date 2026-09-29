import logging
from typing import Optional

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR, settings
from app.models import PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout


logger = logging.getLogger(__name__)


router = APIRouter()

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


def create_comic(
    request_data: PromptRequest,
):
    """
    Complete ComicCraft generation pipeline.
    """

    outline = generate_outline(
        request_data
    )

    stories = generate_story(
        request_data,
        outline,
    )

    image_paths = []

    for panel in stories:

        image_path = generate_image(
            prompt=panel.image_prompt,
            panel_number=panel.panel_number,
        )

        image_paths.append(image_path)

    layout = build_comic_layout(
        stories,
        image_paths,
    )

    pdf_url = save_pdf(
        layout
    )

    return layout, pdf_url


@router.get(
    "/",
    response_class=HTMLResponse,
)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.app_name,
        },
    )


@router.post(
    "/generate",
    response_class=HTMLResponse,
)
async def generate_comic_form(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):

    try:

        prompt_request = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        layout, pdf_url = create_comic(
            prompt_request
        )

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_url": pdf_url,
                "request_data": prompt_request,
            },
        )

    except Exception as exc:

        logger.exception(
            "Comic generation failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Comic generation failed. "
                f"Details: {exc}"
            ),
        )


@router.post(
    "/generate-comic/json"
)
async def generate_comic_json(
    request_data: PromptRequest,
):

    try:

        layout, pdf_url = create_comic(
            request_data
        )

        return JSONResponse(
            content={
                "success": True,
                "message": (
                    "Comic generated successfully."
                ),
                "panels": [
                    panel.model_dump()
                    for panel in layout
                ],
                "pdf_url": pdf_url,
            }
        )

    except Exception as exc:

        logger.exception(
            "JSON comic generation failed."
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get(
    "/test-image",
    response_class=HTMLResponse,
)
async def test_image(
    request: Request,
    prompt: Optional[str] = None,
):

    if not prompt:
        prompt = (
            "A brave fox standing in an "
            "enchanted forest, colorful comic "
            "book illustration"
        )

    try:

        image_path = generate_image(
            prompt=prompt,
            panel_number=0,
        )

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": [],
                "pdf_url": None,
                "test_image": image_path,
            },
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get(
    "/export-success",
    response_class=HTMLResponse,
)
async def export_success(
    request: Request,
    pdf_url: Optional[str] = None,
):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "pdf_url": pdf_url,
        },
    )


@router.get("/health")
async def health():

    return {
        "status": "ok",
        "application": settings.app_name,
        "version": settings.app_version,
    }