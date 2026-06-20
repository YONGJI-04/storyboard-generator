import os
import uuid
import base64
import json
import requests
import anthropic
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
HF_API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
OUTPUT_DIR = Path("/workspace/jiyong/storyboard-generator/outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Storyboard Generator API", description="이야기를 스토리보드로 시각화합니다", version="1.1.0")

class StoryRequest(BaseModel):
    story: str
    num_scenes: int = 3
    save_images: bool = False

@app.get("/")
def root():
    return {"status": "running", "message": "Storyboard Generator API"}

@app.post("/generate")
def generate_storyboard(req: StoryRequest):
    if not 2 <= req.num_scenes <= 5:
        raise HTTPException(status_code=400, detail="장면 수는 2-5 사이여야 합니다")

    scene_res = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": f"""다음 이야기를 {req.num_scenes}개의 장면으로 나누어 JSON 배열로 반환해주세요.
각 장면은 다음 형식으로: [{{"scene_number": 1, "title": "장면 제목", "description": "장면 설명 (한국어)", "visual_prompt": "FLUX.1용 영어 이미지 프롬프트 (30단어 이내)"}}]
JSON만 반환하세요.

이야기: {req.story}"""}]
    )
    scenes = json.loads(scene_res.content[0].text)

    results = []
    for scene in scenes:
        hf_res = requests.post(HF_API_URL, headers={"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}, json={"inputs": scene["visual_prompt"], "parameters": {"width": 768, "height": 512}}, timeout=120)
        image_b64 = None
        saved_path = None

        if hf_res.status_code == 200:
            image_b64 = base64.b64encode(hf_res.content).decode("utf-8")
            if req.save_images:
                filename = f"scene_{scene['scene_number']}_{uuid.uuid4().hex[:8]}.png"
                filepath = OUTPUT_DIR / filename
                with open(filepath, "wb") as f:
                    import io; from PIL import Image; img = Image.open(io.BytesIO(hf_res.content)); img.save(filepath)
                saved_path = str(filepath)

        results.append({**scene, "image_base64": image_b64, "saved_path": saved_path})

    return {"story": req.story, "num_scenes": len(results), "save_images": req.save_images, "scenes": results}

@app.get("/outputs")
def list_outputs():
    files = list(OUTPUT_DIR.glob("*.png"))
    return {"count": len(files), "files": [f.name for f in files]}
