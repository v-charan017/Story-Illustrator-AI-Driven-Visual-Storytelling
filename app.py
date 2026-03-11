import os
from dotenv import load_dotenv
import streamlit as st
from story.image_gen import render_images
from story.splitter import story_to_prompts

load_dotenv()

st.set_page_config(page_title="Story Illustrator", layout="wide")
st.title("Story Illustrator")

with st.expander("Advanced"):
    api_key = st.text_input("Gemini / Google AI Studio API Key (optional if set in env as GOOGLE_API_KEY)", type="password")
    model_id = st.text_input("Imagen model ID", value="imagen-4.0-generate-001")

story_text = st.text_area("Paste your full story", height=220, placeholder="Paste the entire story here...")
col1, col2, col3 = st.columns([1,1,1])
with col1:
    max_frames = st.slider("Frames", min_value=2, max_value=24, value=8, step=1)
with col2:
    style = st.selectbox("Visual style", [
        "cinematic concept art",
        "watercolor children's book",
        "noir graphic novel",
        "anime",
        "storybook pastel",
        "photorealistic"
    ], index=0)
with col3:
    size = st.selectbox("Image size", ["768x768", "1024x1024"], index=1)

split_mode = st.radio("Split story by", ["paragraphs", "sentences"], horizontal=True)

generate = st.button("Generate Story Images", type="primary", disabled=not story_text.strip())

if generate:
    try:
        with st.spinner("Preparing visual prompts..."):
            prompts = story_to_prompts(story_text, max_frames=max_frames, style=style, split_mode=split_mode)
        if not prompts:
            st.warning("No prompts generated. Please try different seed text.")
        else:
            with st.spinner("Rendering images..."):
                images = render_images(prompts, size=size, api_key=api_key or None, model_id=model_id)
            st.subheader("Your story (images only)")
            cols = st.columns(2)
            for i, img in enumerate(images):
                cols[i % 2].image(img, use_container_width=True)
    except Exception as e:
        st.error(f"Error: {e}")
