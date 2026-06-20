# Storyboard Generator

스토리를 입력하면 **Claude API**가 장면을 분할하고 **FLUX.1**이 각 장면 이미지를 생성하는 AI 스토리보드 제작 API

---

## 프로젝트 개요

영화, 애니메이션, 광고 등의 스토리보드 제작을 자동화합니다. Claude가 스토리를 장면으로 나누고 각 장면의 시각적 묘사와 이미지 프롬프트를 생성하며, FLUX.1이 각 장면 이미지를 만들어냅니다.

---

## 아키텍처

```
스토리 텍스트 + 장면 수 (2-5개) 입력
            ↓
    [ Claude API ]
    claude-sonnet-4-6
    스토리 → N개 장면 분할
    각 장면 설명 (한국어) + 이미지 프롬프트 (영어) 생성
            ↓
    각 장면별 FLUX.1-schnell 이미지 생성 (병렬)
            ↓
    장면 설명 + 이미지(Base64) 배열 반환
```

---

## 사용 기술 스택

| 기술 | 역할 |
|------|------|
| **Claude API** (claude-sonnet-4-6) | 스토리 분석 + 장면 구성 + 프롬프트 생성 |
| **FLUX.1-schnell** | 장면별 이미지 생성 |
| **FastAPI** | REST API 서버 |

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/` | 서버 상태 확인 |
| `POST` | `/generate` | 스토리보드 생성 |
| `GET` | `/docs` | Swagger UI |

---

## 요청 / 응답 예시

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "story": "우주비행사가 낯선 행성에 착륙해 외계 생명체와 교신에 성공하는 이야기",
    "num_scenes": 3
  }'
```

**응답:**

```json
{
  "story": "우주비행사가 낯선 행성에...",
  "scenes": [
    {
      "scene_number": 1,
      "description": "우주선이 붉고 황량한 외계 행성 표면에 착륙하는 장면",
      "image_prompt": "spaceship landing on alien red planet, dust storm, dramatic sky, cinematic, detailed",
      "image_base64": "iVBORw0KGgo..."
    },
    {
      "scene_number": 2,
      "description": "우주복을 입은 비행사가 낯선 외계 생명체와 마주치는 장면",
      "image_prompt": "astronaut meeting alien creature, tense first contact, sci-fi, cinematic lighting",
      "image_base64": "iVBORw0KGgo..."
    },
    {
      "scene_number": 3,
      "description": "비행사와 외계 생명체가 홀로그램으로 교신하는 장면",
      "image_prompt": "astronaut and alien communicating via hologram, blue light, futuristic, hopeful",
      "image_base64": "iVBORw0KGgo..."
    }
  ]
}
```

---

## 제한사항

- 장면 수: **2~5개** (API 비용 및 응답 시간 고려)

---

## 실행 방법

```bash
cp .env.example .env
pip install -r requirements.txt
cd app && uvicorn main:app --host 0.0.0.0 --port 8007
```

## 환경 변수

| 변수 | 설명 |
|------|------|
| `ANTHROPIC_API_KEY` | Anthropic Claude API 키 |
| `HF_TOKEN` | HuggingFace API 토큰 |
