import os
import requests
import base64
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic

load_dotenv()

app = FastAPI(title="Storyboard Generator API")
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
HF_API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"


class StoryRequest(BaseModel):
    story: str
    num_scenes: int = 3


@app.get("/")
def root():
    return {"status": "running", "message": "Storyboard Generator API"}


@app.post("/generate")
def generate_storyboard(req: StoryRequest):
    if not req.story.strip():
        raise HTTPException(status_code=400, detail="스토리를 입력해주세요")
    if not 2 <= req.num_scenes <= 5:
        raise HTTPException(status_code=400, detail="장면 수는 2-5개 사이여야 합니다")

    scenes_msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""다음 스토리를 {req.num_scenes}개의 장면으로 나눠주세요.

스토리: {req.story}

각 장면을 다음 형식으로 작성해주세요:
SCENE 1:
설명: (한국어로 장면 설명)
프롬프트: (영어 이미지 생성 프롬프트, cinematic style, detailed)

SCENE 2:
...

프롬프트는 영어로, 설명은 한국어로 작성해주세요."""
        }]
    )

    content = scenes_msg.content[0].text
    scenes = []

    for i in range(1, req.num_scenes + 1):
        scene_text = ""
        if f"SCENE {i}:" in content:
            start = content.index(f"SCENE {i}:")
            end = content.index(f"SCENE {i+1}:") if i < req.num_scenes and f"SCENE {i+1}:" in content else len(content)
            scene_text = content[start:end]

        description = ""
        image_prompt = f"cinematic scene {i}, high quality"

        for line in scene_text.split("\n"):
            if "설명:" in line:
                description = line.replace("설명:", "").strip()
            elif "프롬프트:" in line:
                image_prompt = line.replace("프롬프트:", "").strip()

        headers = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}
        image_resp = requests.post(HF_API_URL, headers=headers, json={"inputs": image_prompt}, timeout=120)
        image_b64 = base64.b64encode(image_resp.content).decode("utf-8") if image_resp.status_code == 200 else None

        scenes.append({
            "scene_number": i,
            "description": description,
            "image_prompt": image_prompt,
            "image_base64": image_b64,
        })

    return JSONResponse(content={"story": req.story, "scenes": scenes})
