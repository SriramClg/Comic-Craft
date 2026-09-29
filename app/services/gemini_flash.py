import json
import logging
from typing import List

from app.config import settings
from app.models import PanelOutline, PromptRequest


logger = logging.getLogger(__name__)


def _fallback_outline(request: PromptRequest) -> List[PanelOutline]:
    """
    Offline fallback used when Gemini is unavailable.
    """

    character = request.character_name
    setting = request.setting
    tone = request.tone
    style = request.art_style

    return [
        PanelOutline(
            panel_number=1,
            title="The Beginning",
            scene_description=(
                f"{character} begins the adventure in the {setting}. "
                f"The atmosphere is {tone}."
            ),
            image_prompt=(
                f"Comic book illustration of {character} at the beginning "
                f"of an adventure in {setting}, {style} style, "
                f"cinematic composition, expressive character."
            ),
        ),
        PanelOutline(
            panel_number=2,
            title="A Strange Discovery",
            scene_description=(
                f"{character} discovers something unusual while exploring "
                f"the {setting}."
            ),
            image_prompt=(
                f"{character} discovering something mysterious in {setting}, "
                f"{style} comic illustration, dramatic lighting, "
                f"expressive face."
            ),
        ),
        PanelOutline(
            panel_number=3,
            title="The Challenge",
            scene_description=(
                f"A challenge appears and {character} must decide "
                f"what to do next."
            ),
            image_prompt=(
                f"{character} facing a major challenge in {setting}, "
                f"{style} comic book artwork, dynamic action scene."
            ),
        ),
        PanelOutline(
            panel_number=4,
            title="The Turning Point",
            scene_description=(
                f"{character} finds a creative way to overcome the "
                f"challenge."
            ),
            image_prompt=(
                f"{character} overcoming a challenge in {setting}, "
                f"{style} comic illustration, heroic pose, "
                f"dramatic cinematic scene."
            ),
        ),
        PanelOutline(
            panel_number=5,
            title="A New Beginning",
            scene_description=(
                f"{character}'s adventure reaches a satisfying conclusion "
                f"and hints at another adventure."
            ),
            image_prompt=(
                f"{character} standing proudly after the adventure in "
                f"{setting}, {style} comic book ending scene, "
                f"beautiful cinematic composition."
            ),
        ),
    ]


def generate_outline(request: PromptRequest) -> List[PanelOutline]:
    """
    Generate a structured five-panel comic outline using Gemini Flash.

    If no Gemini API key is configured, a deterministic fallback outline
    is returned so that the application remains runnable locally.
    """

    if not settings.gemini_api_key:
        logger.warning(
            "GEMINI_API_KEY is not configured. Using fallback outline."
        )
        return _fallback_outline(request)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.gemini_api_key)

        prompt = f"""
You are the outline writer for ComicCraft.

Create a coherent {settings.panels_count}-panel comic outline.

User story:
{request.story_prompt}

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Requirements:

1. Exactly {settings.panels_count} panels.
2. Keep the same main character throughout.
3. Maintain continuity between panels.
4. Each panel needs:
   - panel_number
   - title
   - scene_description
   - image_prompt
5. Image prompts must be detailed enough for an image-generation model.
6. Do not include markdown.
7. Return valid JSON only.

The JSON must be an array of objects.
"""

        response = client.models.generate_content(
            model=settings.gemini_flash_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.9,
                response_mime_type="application/json",
            ),
        )

        data = json.loads(response.text)

        panels = [
            PanelOutline.model_validate(item)
            for item in data
        ]

        if len(panels) != settings.panels_count:
            raise ValueError(
                f"Gemini returned {len(panels)} panels instead of "
                f"{settings.panels_count}."
            )

        return panels

    except Exception as exc:
        logger.exception(
            "Gemini outline generation failed: %s",
            exc,
        )

        return _fallback_outline(request)