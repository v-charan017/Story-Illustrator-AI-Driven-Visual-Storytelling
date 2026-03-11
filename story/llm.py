import json
from typing import List, Optional
import os
import google.generativeai as genai

SYSTEM = (
    "You are a storyboard writer. Given seed lines of a story, you analyze and expand them into a coherent, emotionally engaging arc. "
    "Return only compact JSON with a 'prompts' array where each element is a stable, detailed image prompt describing a single scene. "
    "No dialogue text; focus on vivid visual details, composition, lighting, mood, characters, and setting. Keep character appearances consistent across frames."
)

SCHEMA_HINT = (
    "Respond as JSON: {\n"
    "  \"prompts\": [\n"
    "    { \"scene\": 1, \"prompt\": \"...\" }\n"
    "  ]\n"
    "}"
)

def _configure(api_key: Optional[str] = None) -> None:
    key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Provide GOOGLE_API_KEY (or GEMINI_API_KEY) via env or UI.")
    genai.configure(api_key=key)


def generate_storyboard(
    seed: str,
    max_frames: int = 8,
    style: str = "cinematic concept art",
    api_key: Optional[str] = None,
    model_id: str = "gemini-1.5-flash-8b",
) -> List[str]:
    seed = seed.strip()
    if not seed:
        return []
    _configure(api_key)
    model = genai.GenerativeModel(model_id)
    user = (
        f"Seed lines: {seed}\n"
        f"Target number of frames: {max_frames}\n"
        f"Visual style to apply consistently: {style}\n\n"
        "Produce between 6 and the target number of frames (inclusive) as needed. "
        "Each prompt must be self-contained, descriptive, and avoid text overlays, captions, or typography. "
        "Ensure continuity of main characters (names, attire, physical traits) and the setting across scenes.\n\n"
        f"{SCHEMA_HINT}"
    )
    prompt = f"System: {SYSTEM}\nUser: {user}"
    resp = model.generate_content(prompt)
    text = resp.text
    try:
        data = json.loads(text)
    except Exception:
        # Retry with JSON instruction appended if model returned prose
        resp2 = model.generate_content(prompt + "\nReturn ONLY valid JSON as specified.")
        data = json.loads(resp2.text)
    prompts = data.get("prompts", [])
    prompts = [p.get("prompt", "") for p in prompts if isinstance(p, dict)]
    prompts = [p for p in prompts if p]
    if len(prompts) > max_frames:
        prompts = prompts[:max_frames]
    return prompts
