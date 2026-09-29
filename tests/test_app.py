import os

os.environ["IMAGE_BACKEND"] = "placeholder"
os.environ["GEMINI_API_KEY"] = ""


from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_homepage():

    response = client.get("/")

    assert response.status_code == 200

    assert "ComicCraft" in response.text


def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_generate_comic_json():

    payload = {
        "story_prompt": (
            "A brave fox explores an enchanted forest."
        ),
        "character_name": "Finn",
        "setting": "enchanted forest",
        "tone": "funny",
        "art_style": "comic book",
    }

    response = client.post(
        "/generate-comic/json",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert len(data["panels"]) == 5

    assert data["pdf_url"].endswith(".pdf")