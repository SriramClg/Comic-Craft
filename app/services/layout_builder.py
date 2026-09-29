from typing import List

from app.models import ComicPanel, PanelStory


def build_comic_layout(
    stories: List[PanelStory],
    image_paths: List[str],
) -> List[ComicPanel]:

    if len(stories) != len(image_paths):
        raise ValueError(
            "Number of stories and images must match."
        )

    layout = []

    for story, image_path in zip(
        stories,
        image_paths,
    ):
        layout.append(
            ComicPanel(
                panel_number=story.panel_number,
                title=story.title,
                image_path=image_path,
                scene_description=story.scene_description,
                caption=story.caption,
                narration=story.narration,
                dialogue=story.dialogue,
                image_prompt=story.image_prompt,
            )
        )

    return layout