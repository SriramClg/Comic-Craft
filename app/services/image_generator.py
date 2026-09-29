import logging
import re
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from app.config import BASE_DIR, settings


logger = logging.getLogger(__name__)


PANELS_DIR = BASE_DIR / "static" / "panels"
PANELS_DIR.mkdir(parents=True, exist_ok=True)


def _safe_filename(value: str) -> str:
    value = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        value,
    )

    return value.strip("_")[:80] or "panel"


def _create_placeholder(
    prompt: str,
    panel_number: int,
) -> str:

    filename = (
        f"panel_{panel_number}_"
        f"{_safe_filename(prompt[:35])}.png"
    )

    path = PANELS_DIR / filename

    width = settings.image_width
    height = settings.image_height

    image = Image.new(
        "RGB",
        (width, height),
        (235, 225, 205),
    )

    draw = ImageDraw.Draw(image)

    # Border
    draw.rectangle(
        (15, 15, width - 15, height - 15),
        outline=(30, 30, 30),
        width=8,
    )

    title = f"ComicCraft - Panel {panel_number}"

    try:
        font = ImageFont.truetype(
            "arial.ttf",
            36,
        )

        small_font = ImageFont.truetype(
            "arial.ttf",
            20,
        )

    except OSError:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    draw.text(
        (40, 40),
        title,
        fill=(20, 20, 20),
        font=font,
    )

    # Simple comic-style speech bubble
    bubble = (
        70,
        150,
        width - 70,
        300,
    )

    draw.rounded_rectangle(
        bubble,
        radius=25,
        fill=(255, 255, 255),
        outline=(20, 20, 20),
        width=4,
    )

    text = (
        "Image generation placeholder.\n"
        "Configure IMAGE_BACKEND=diffusers\n"
        "to generate AI artwork."
    )

    draw.multiline_text(
        (100, 185),
        text,
        fill=(20, 20, 20),
        font=small_font,
        spacing=10,
    )

    # Prompt reference at bottom
    preview = prompt[:100]

    draw.text(
        (40, height - 70),
        preview,
        fill=(60, 60, 60),
        font=small_font,
    )

    image.save(path)

    return f"/static/panels/{filename}"


_diffusion_pipeline = None


def _get_diffusion_pipeline():
    global _diffusion_pipeline

    if _diffusion_pipeline is not None:
        return _diffusion_pipeline

    import torch
    from diffusers import StableDiffusionPipeline

    dtype = (
        torch.float16
        if torch.cuda.is_available()
        else torch.float32
    )

    logger.info(
        "Loading Diffusers model: %s",
        settings.image_model,
    )

    pipeline = StableDiffusionPipeline.from_pretrained(
        settings.image_model,
        torch_dtype=dtype,
    )

    if torch.cuda.is_available():
        pipeline = pipeline.to("cuda")

    _diffusion_pipeline = pipeline

    return pipeline


def _generate_with_diffusers(
    prompt: str,
    panel_number: int,
) -> str:

    pipeline = _get_diffusion_pipeline()

    result = pipeline(
        prompt=prompt,
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=25,
        guidance_scale=7.5,
    )

    image = result.images[0]

    filename = (
        f"panel_{panel_number}_"
        f"{_safe_filename(prompt[:35])}.png"
    )

    path = PANELS_DIR / filename

    image.save(path)

    return f"/static/panels/{filename}"


def generate_image(
    prompt: str,
    panel_number: int,
) -> str:
    """
    Generate a comic illustration.

    Supported IMAGE_BACKEND values:

    placeholder
    diffusers
    auto
    """

    backend = settings.image_backend.lower().strip()

    if backend == "placeholder":
        return _create_placeholder(
            prompt,
            panel_number,
        )

    if backend == "diffusers":
        try:
            return _generate_with_diffusers(
                prompt,
                panel_number,
            )

        except Exception as exc:
            logger.exception(
                "Diffusers image generation failed: %s",
                exc,
            )

            return _create_placeholder(
                prompt,
                panel_number,
            )

    if backend == "auto":
        try:
            return _generate_with_diffusers(
                prompt,
                panel_number,
            )

        except Exception as exc:
            logger.warning(
                "Auto image generation failed. "
                "Using placeholder: %s",
                exc,
            )

            return _create_placeholder(
                prompt,
                panel_number,
            )

    logger.warning(
        "Unknown IMAGE_BACKEND=%s. "
        "Using placeholder.",
        backend,
    )

    return _create_placeholder(
        prompt,
        panel_number,
    )