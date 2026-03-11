import re
from typing import List

_DEF_STYLE_SUFFIX = {
    "cinematic concept art": "cinematic concept art, dramatic lighting, volumetric light, high detail, 8k concept art, ultra-detailed, no text",
    "watercolor children's book": "soft watercolor illustration, gentle colors, children's book style, simple shapes, clean background, no text",
    "noir graphic novel": "black and white noir graphic novel, stark contrast, moody lighting, film grain, no speech bubbles, no text",
    "anime": "anime style, clean line art, vibrant colors, dynamic composition, no subtitles, no text",
    "storybook pastel": "pastel storybook illustration, soft shading, whimsical, textured paper feel, no text",
    "photorealistic": "photorealistic, natural lighting, shallow depth of field, high detail, no text"
}


def _split_paragraphs(text: str) -> List[str]:
    # Split on 1+ blank lines
    blocks = re.split(r"\n\s*\n+", text.strip(), flags=re.MULTILINE)
    return [b.strip() for b in blocks if b.strip()]


def _split_sentences(text: str) -> List[str]:
    # Lightweight sentence split (., !, ?) followed by space or EOL
    # Keep punctuation with sentence
    parts = re.split(r"(?<=[\.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _select_slices(items: List[str], max_frames: int) -> List[str]:
    if len(items) <= max_frames:
        return items
    # Evenly sample max_frames items across the list
    idxs = [round(i * (len(items) - 1) / (max_frames - 1)) for i in range(max_frames)]
    seen = set()
    result = []
    for i in idxs:
        if i not in seen:
            result.append(items[i])
            seen.add(i)
    # If duplicates due to rounding, fill gaps
    j = 0
    while len(result) < max_frames and j < len(items):
        if j not in seen:
            result.append(items[j])
        j += 1
    return result[:max_frames]


def _build_prompt(chunk: str, style: str) -> str:
    style_suffix = _DEF_STYLE_SUFFIX.get(style, _DEF_STYLE_SUFFIX["cinematic concept art"])
    base = (
        "Illustrate the following story beat as a single image. Focus on visual elements only; include no text, captions, or typography. "
        "Show character consistency across frames if characters are described."
    )
    return f"{base} Scene description: {chunk}. Visual style: {style_suffix}."


def story_to_prompts(text: str, max_frames: int = 8, style: str = "cinematic concept art", split_mode: str = "paragraphs") -> List[str]:
    text = text.strip()
    if not text:
        return []
    if split_mode == "sentences":
        chunks = _split_sentences(text)
    else:
        chunks = _split_paragraphs(text)
    if not chunks:
        return []
    selected = _select_slices(chunks, max_frames)
    prompts = [_build_prompt(c, style) for c in selected]
    return prompts
