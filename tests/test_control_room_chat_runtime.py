from pathlib import Path
from types import SimpleNamespace

from brain.control_room.chat_runtime import OpenAIAdvisoryRuntime


class FakeResponses:
    def __init__(self):
        self.payload = None

    def create(self, **payload):
        self.payload = payload
        return SimpleNamespace(output_text="Reviewed")


def test_openai_runtime_forwards_text_and_image_attachments(tmp_path: Path):
    image_path = tmp_path / "reference.png"
    image_path.write_bytes(b"png-bytes")
    responses = FakeResponses()
    client = SimpleNamespace(responses=responses)
    runtime = OpenAIAdvisoryRuntime(model="test-model", client=client)
    agent = {
        "name": "Creative Spatial",
        "mission": "Review spatial intent.",
        "skills": [],
        "prohibited_actions": [],
    }
    attachments = [
        {
            "filename": "brief.txt",
            "content_type": "text/plain",
            "storage_path": str(tmp_path / "unused.txt"),
            "extracted_text": "Height is 5500 mm.",
        },
        {
            "filename": "reference.png",
            "content_type": "image/png",
            "storage_path": str(image_path),
            "extracted_text": None,
        },
    ]
    history = [{"role": "user", "content": "Review these", "attachments": []}]

    result = runtime.respond(
        agent=agent,
        message="Review these",
        history=history,
        attachments=attachments,
    )

    blocks = responses.payload["input"][0]["content"]
    assert result == "Reviewed"
    assert blocks[0] == {"type": "input_text", "text": "Review these"}
    assert blocks[1]["type"] == "input_text"
    assert "Height is 5500 mm." in blocks[1]["text"]
    assert blocks[2]["type"] == "input_image"
    assert blocks[2]["image_url"].startswith("data:image/png;base64,")
