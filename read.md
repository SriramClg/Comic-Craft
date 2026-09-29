# ComicCraft

ComicCraft is an AI-powered comic story creator.

Users provide:

- Story prompt
- Main character
- Setting
- Story tone
- Art style

The application generates:

1. A five-panel comic outline
2. Narration
3. Dialogue
4. Captions
5. Comic illustrations
6. A downloadable PDF

## Technology

### Frontend

- HTML5
- CSS3
- Jinja2

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic

### AI

- Google Gemini
- Gemini Flash
- Gemini Pro
- Hugging Face Diffusers
- Stable Diffusion

### Export

- FPDF2
- Pillow

## Project Structure

```text
ComicCraft/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── routes.py
│   │
│   └── services/
│       ├── gemini_flash.py
│       ├── gemini_pro.py
│       ├── image_generator.py
│       ├── layout_builder.py
│       └── exporters.py
│
├── templates/
│   ├── index.html
│   ├── comic_preview.html
│   └── export_success.html
│
├── static/
│   ├── css/
│   ├── panels/
│   └── exports/
│
├── tests/
│   └── test_app.py
│
├── .env
├── .env.example
├── requirements.txt
└── run.ps1