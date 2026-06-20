# Storyboard Generator

스토리를 입력하면 Claude가 장면을 나누고 FLUX.1이 각 장면 이미지를 생성하는 API

## 아키텍처

```
스토리 텍스트 + 장면 수 입력
        ↓
Claude API - 장면 분할 + 각 장면 설명 + 이미지 프롬프트 생성
        ↓
HuggingFace FLUX.1-schnell - 장면별 이미지 생성
        ↓
장면 설명 + 이미지(base64) 배열 반환
```

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/` | 서버 상태 확인 |
| POST | `/generate` | 스토리보드 생성 |
| GET | `/docs` | Swagger UI |

## 요청 예시

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "story": "우주비행사가 낯선 행성에 착륙해 외계 생명체를 만나는 이야기",
    "num_scenes": 3
  }'
```

## 응답 예시

```json
{
  "story": "우주비행사가 ...",
  "scenes": [
    {
      "scene_number": 1,
      "description": "우주선이 붉은 행성에 착륙하는 장면",
      "image_prompt": "spaceship landing on alien planet...",
      "image_base64": "iVBORw0KGgo..."
    }
  ]
}
```

## 제한사항

- 장면 수: 2~5개

## 실행 방법

```bash
cp .env.example .env
pip install -r requirements.txt
cd app && uvicorn main:app --host 0.0.0.0 --port 8007
```

## 환경 변수

```
ANTHROPIC_API_KEY=   # Anthropic Claude API 키
HF_TOKEN=            # HuggingFace API 토큰
```
