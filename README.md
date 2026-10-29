# Story Illustrator: AI-Driven Visual Storytelling

Story Illustrator is a full-stack AI application that transforms raw narrative text into a series of high-fidelity, consistent visual storyboards. This project leverages **Google's Gemini and Imagen models** to automate the creative process of "story-to-concept-art."

## Features
* **Intelligent Text Analysis:** Automatically splits complex stories into key "beats" using NLP logic.
* **Multi-Model Integration:** * **Gemini 1.5 Flash:** Orchestrates storyboard logic and prompt engineering.
    * **Imagen 4.0:** Renders high-resolution (1024x1024) images with artistic style consistency.
* **Dynamic Art Styles:** Supports multiple visual aesthetics, including Cinematic Concept Art, Noir Graphic Novel, Anime, and Watercolor.
* **Production-Ready UI:** Built with **Streamlit** for a responsive, headless-ready user experience.

## Tech Stack
* Language: Python 3.9+
* Frontend: Streamlit
* AI/ML: Google Generative AI (Gemini API), Vertex AI (Imagen)
* Image Processing: Pillow (PIL)
* Environment: Virtualenv, Dotenv

## Project Structure
* `app.py`: Main Streamlit application and UI logic.
* `story`:
    * `image_gen.py`: Advanced API wrappers for Google’s image generation models.
    * `splitter.py`: Logic for text segmentation and visual prompt construction.
    * `llm.py`: Direct integration with LLMs for storyboard planning.

## Quick Start

1. **Clone & Setup:**
```
mkdir story-illustrator
cd story-illustrator
git clone https://github.com/v-charan017/Story-Illustrator-AI-Driven-Visual-Storytelling
```
---

## Setup (in Detail)
If you dont have Python 3.9 above or 3.12 below then:
On mac
```
brew install python@3.12
```
On linux:
```
sudo apt install python3.12 -y
```
Or any version of your choice within the mentioned range.  

1. (Recommended) Create and activate a virtual environment.

```
python3 -m venv .venv
source .venv/bin/activate
```
2. Install dependencies:

```
pip install -r requirements.txt
```

3. Set your Google AI Studio key (copy `.env.example` to `.env` or export):

```
export GOOGLE_API_KEY="your_key_here"
```

## Run

From this folder:
```
streamlit run app.py
```

Paste your full story. The app will split it into beats and generate images to tell the story visually using Google Imagen.

## Quick Commands

- Kill anything using port 8501:
```
lsof -ti:8501 | xargs kill -9
```

- Launch the app on port 8501 (headless):
```
.venv/bin/streamlit run app.py --server.port 8501 --server.headless true
```

- Open in your browser:
```
http://localhost:8501
```
---

# Origin
It demonstrates application of GenAI workflow, API integration and prompt engineering.
