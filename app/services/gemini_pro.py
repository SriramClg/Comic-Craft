import json
import logging
from typing import List

from app.config import settings
from app.models import PanelOutline, PanelStory, PromptRequest


logger = logging.getLogger(__name__)


def _fallback_story(
    request: PromptRequest,
    outline: List[PanelOutline],
) -> List[PanelStory]:

    stories = []

    for panel in outline:
        stories.append(
            PanelStory(
                panel_number=panel.panel_number,
                title=panel.title,
                scene_description=panel.scene_description,
                image_prompt=panel.image_prompt,
                caption=(
                    f"The adventure continues in the "
                    f"{request.setting}."
                ),
                narration=(
                    f"{request.character_name} takes a deep breath "
                    f"and moves forward, determined to discover "
                    f"what comes next."
                ),
                dialogue=(
                    f"{request.character_name}: "
                    f"\"I have to keep going!\""
                ),
            )
        )

    return stories


def generate_story(
    request: PromptRequest,
    outline: List[PanelOutline],
) -> List[PanelStory]:
    """
    Expand the outline into full comic narration and dialogue.
    """

    if not settings.gemini_api_key:
        logger.warning(
            "GEMINI_API_KEY is not configured. Using fallback story."
        )
        return _fallback_story(request, outline)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.gemini_api_key)

        outline_json = json.dumps(
            [
                panel.model_dump()
                for panel in outline
            ],
            indent=2,
        )

        prompt = f"""
You are the professional comic writer for ComicCraft.

Create the complete narration and dialogue for this comic.

Original story prompt:
{request.story_prompt}

Character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Panel outline:
{outline_json}

For every panel produce:

- panel_number
- title
- scene_description
- image_prompt
- caption
- narration
- dialogue

Requirements:

1. Preserve continuity.
2. Keep the main character consistent.
3. Match the requested tone.
4. Make dialogue natural and concise.
5. Make narration cinematic.
6. Captions should work visually as comic captions.
7. Do not use markdown.
8. Return valid JSON only.
9. Return exactly one object for every outline panel.
"""

        response = client.models.generate_content(
            model=settings.gemini_pro_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.9,
                response_mime_type="application/json",
            ),
        )

        data = json.loads(response.text)

        stories = [
            PanelStory.model_validate(item)
            for item in data
        ]

        if len(stories) != len(outline):
            raise ValueError(
                "Gemini story response does not match outline."
            )

        return stories

    except Exception as exc:
        logger.exception(
            "Gemini story generation failed: %s",
            exc,
        )

        return _fallback_story(request, outline)