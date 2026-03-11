from io import BytesIO
from typing import List, Optional, Tuple
from PIL import Image
import os
import base64
import requests
import google.generativeai as genai

def _get_api_key(explicit: Optional[str]) -> str:
    key = explicit or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Provide GOOGLE_API_KEY (or GEMINI_API_KEY) via env or UI.")
    return key

def _parse_size(size: str) -> Tuple[int, int]:
    try:
        w, h = size.lower().split("x")
        return int(w), int(h)
    except Exception:
        return 1024, 1024

def _call_imagen_api(model_id: str, prompt: str, api_key: str, size: str) -> bytes:
    # Prefer plural method name used by v1beta for Imagen 4.0
    base = "https://generativelanguage.googleapis.com/v1beta"
    url = f"{base}/models/{model_id}:generateImages?key={api_key}"
    width, height = _parse_size(size)
    payload = {
        "prompt": {"text": prompt},
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "width": width,
            "height": height,
        },
    }
    headers = {"Content-Type": "application/json"}
    r = requests.post(url, json=payload, headers=headers, timeout=120)
    if r.status_code == 404:
        # Fallback to singular endpoint for older models
        url2 = f"{base}/models/{model_id}:generateImage?key={api_key}"
        r = requests.post(url2, json=payload, headers=headers, timeout=120)
        if r.status_code >= 400:
            raise RuntimeError(f"Imagen API error {r.status_code} at {url2}: {r.text}")
    elif r.status_code >= 400:
        raise RuntimeError(f"Imagen API error {r.status_code} at {url}: {r.text}")
    data = r.json()
    # Try common response shapes
    # 1) generatedImages: [{ 'image': { 'bytesBase64Encoded': '...' } }]
    if isinstance(data, dict) and "generatedImages" in data:
        arr = data.get("generatedImages") or []
        if arr:
            img_node = arr[0].get("image") or {}
            b64 = img_node.get("bytesBase64Encoded")
            if b64:
                return base64.b64decode(b64)
    # 2) images: ['base64...'] or [{'bytesBase64Encoded': '...'}]
    if isinstance(data, dict) and "images" in data:
        arr = data.get("images") or []
        if arr:
            first = arr[0]
            if isinstance(first, str):
                return base64.b64decode(first)
            if isinstance(first, dict):
                b64 = first.get("bytesBase64Encoded")
                if b64:
                    return base64.b64decode(b64)
    raise RuntimeError("No image bytes found in Imagen API response")

def _call_gemini_flash_image(model_id: str, prompt: str, api_key: str) -> bytes:
    # Use Gemini image generation models via SDK, extract inline image bytes
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_id)
    resp = model.generate_content(prompt)
    # Look through parts for inline image data
    if hasattr(resp, "candidates") and resp.candidates:
        for cand in resp.candidates:
            content = getattr(cand, "content", None)
            if not content:
                continue
            parts = getattr(content, "parts", [])
            for p in parts:
                inline = getattr(p, "inline_data", None) or getattr(p, "inlineData", None)
                if inline:
                    mime = getattr(inline, "mime_type", None) or getattr(inline, "mimeType", None)
                    data = getattr(inline, "data", None)
                    if data and isinstance(data, (str, bytes)) and (not mime or mime.startswith("image/")):
                        b = base64.b64decode(data) if isinstance(data, str) else data
                        return b
    # Some SDK versions put images in resp._result or resp.media
    parts = getattr(resp, "parts", []) or getattr(resp, "media", [])
    for p in parts or []:
        data = getattr(p, "data", None)
        if isinstance(data, (bytes, str)):
            return base64.b64decode(data) if isinstance(data, str) else data
    raise RuntimeError("No inline image returned by Gemini model")

def list_imagen_models(api_key: Optional[str] = None) -> list:
    """Return a list of model IDs that appear to support image generation."""
    key = _get_api_key(api_key)
    base = "https://generativelanguage.googleapis.com/v1beta"
    url = f"{base}/models?key={key}"
    r = requests.get(url, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"ListModels error {r.status_code}: {r.text}")
    data = r.json() or {}
    models = data.get("models", [])
    results = []
    for m in models:
        name = m.get("name", "")  # e.g., models/imagen-4.0-generate-001
        # Some responses include supported generation methods
        methods = m.get("supportedGenerationMethods", []) or m.get("supportedMethods", [])
        if ("imagen" in name) or ("image" in "".join(methods).lower()):
            # strip leading 'models/' if present
            model_id = name.split("/", 1)[-1]
            results.append(model_id)
    return sorted(set(results))

def render_images(
    prompts: List[str],
    size: str = "1024x1024",
    api_key: Optional[str] = None,
    model_id: str = "imagen-4.0-generate-001",
) -> List[Image.Image]:
    key = _get_api_key(api_key)
    images: List[Image.Image] = []
    use_gemini_flash = model_id.startswith("gemini-2.5-flash-image")
    for prompt in prompts:
        if use_gemini_flash:
            # Include size hint in prompt, since SDK may not take width/height params
            prompt_with_size = f"{prompt} Render at approximately {size} resolution."
            img_bytes = _call_gemini_flash_image(model_id=model_id, prompt=prompt_with_size, api_key=key)
        else:
            img_bytes = _call_imagen_api(model_id=model_id, prompt=prompt, api_key=key, size=size)
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        images.append(img)
    return images
