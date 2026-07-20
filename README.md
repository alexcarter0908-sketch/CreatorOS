# CreatorOS

An AI-powered content creation platform. CreatorOS lets creators generate scripts, images, videos, audio, SEO content, and documents from a single chat-based "Command Center" — with automatic provider fallback, credit-based billing, multi-step generation pipelines, and YouTube publishing.

## Features

- **Command Center** — a chat interface for generating any content type (text, script, image, video, audio, SEO, documents) from natural-language prompts, with real-time streaming responses.
- **Multi-provider fallback** — generation requests automatically retry across multiple AI providers (e.g. Runway → PixVerse for video) if one fails.
- **Pipelines** — a single request like "make a video for my YouTube channel" can trigger a full script → thumbnail → video → SEO pipeline.
- **Asset Library** — every generated asset is saved and browsable/downloadable later.
- **Billing & credits** — usage-based credit system with an upgrade flow when credits run out.
- **YouTube publishing** — connect a YouTube account and publish generated videos directly.
- **Voice input** — record a voice note and it's transcribed into the prompt box.

## Tech stack

- **Frontend:** Next.js (App Router), TypeScript, Tailwind
- **Backend:** FastAPI (Python), SQLAlchemy, PostgreSQL
- **Infra:** Docker Compose (frontend + backend + db)
- **CI:** GitHub Actions (`.github/workflows/ci.yml`) — runs backend syntax checks and frontend lint + build on every push/PR to `main`.

## Getting started

### Prerequisites

- Docker and Docker Compose
- API keys/credentials for whichever providers are used (Groq, Runway, PixVerse, etc.) — see `backend/.env.example` if present, or ask a maintainer for the required environment variables.

### Run locally

```bash
git clone https://github.com/alexcarter0908-sketch/CreatorOS.git
cd CreatorOS
docker compose up -d --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

### Common commands

```bash
# Rebuild only the frontend after a code change
docker compose up -d --build frontend

# Rebuild only the backend after a code change
docker compose up -d --build backend

# Tail logs
docker compose logs -f frontend
docker compose logs -f backend
```

## Project structure

```
backend/    FastAPI app (API routes, agents, providers, billing, database)
frontend/   Next.js app (pages, features, components)
docs/       Additional documentation
```

## Contributing

This is currently a solo/private-development project. If that changes, add contribution guidelines here.

## License

See [LICENSE](./LICENSE).
