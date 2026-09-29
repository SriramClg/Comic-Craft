from datetime import datetime
from pathlib import Path
from typing import List

from fpdf import FPDF

from app.config import BASE_DIR
from app.models import ComicPanel


EXPORTS_DIR = BASE_DIR / "static" / "exports"
EXPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def _image_filesystem_path(
    image_path: str,
) -> Path:

    clean_path = image_path.lstrip("/")

    return BASE_DIR / clean_path


def save_pdf(
    panels: List[ComicPanel],
) -> str:

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = f"comiccraft_{timestamp}.pdf"

    output_path = EXPORTS_DIR / filename

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    for panel in panels:

        pdf.add_page()

        pdf.set_font(
            "Helvetica",
            "B",
            20,
        )

        pdf.cell(
            0,
            12,
            f"Panel {panel.panel_number}: "
            f"{panel.title}",
            new_x="LMARGIN",
            new_y="NEXT",
            align="C",
        )

        pdf.ln(4)

        image_path = _image_filesystem_path(
            panel.image_path
        )

        if image_path.exists():

            max_width = 180
            max_height = 105

            pdf.image(
                str(image_path),
                x=15,
                y=None,
                w=max_width,
                h=max_height,
            )

            pdf.ln(8)

        pdf.set_font(
            "Helvetica",
            "I",
            11,
        )

        pdf.multi_cell(
            0,
            7,
            panel.scene_description,
        )

        pdf.ln(4)

        pdf.set_font(
            "Helvetica",
            "B",
            11,
        )

        pdf.multi_cell(
            0,
            7,
            f"Caption: {panel.caption}",
        )

        pdf.ln(2)

        pdf.set_font(
            "Helvetica",
            "",
            11,
        )

        pdf.multi_cell(
            0,
            7,
            panel.narration,
        )

        pdf.ln(4)

        pdf.set_font(
            "Helvetica",
            "I",
            11,
        )

        pdf.multi_cell(
            0,
            7,
            panel.dialogue,
        )

    pdf.output(str(output_path))

    return f"/static/exports/{filename}"