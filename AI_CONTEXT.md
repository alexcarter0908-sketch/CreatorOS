# CreatorOS - AI Context

## Project Overview

CreatorOS is a production-ready AI Content Operating System (SaaS).

The goal is to allow creators, agencies and businesses to generate, manage and publish AI-powered content from one dashboard.

---

# Technology Stack

## Backend

- FastAPI
- SQLAlchemy ORM
- SQLite (Development)
- JWT Authentication
- Repository Pattern
- Service Layer
- Pydantic v2

## Frontend

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- Axios
- Zustand

---

# Current Architecture

backend/

- api/
- core/
- database/
- dependencies/
- repositories/
- schemas/
- services/
- middleware/
- utils/

frontend/

- app/
- components/
- lib/
- store/

---

# Coding Rules

Never break existing architecture.

Always use:

Repository
↓

Service
↓

API Router

Never query database directly inside endpoints.

Business logic must stay inside Services.

Database operations must stay inside Repositories.

---

# Authentication

Completed.

Features

- User Registration
- Login
- JWT Authentication
- Protected Routes
- Current User Endpoint

---

# Current Completed Modules

✅ Authentication

✅ Users

✅ Projects (Backend Foundation)

---

# Pending Modules

- Dashboard
- AI Agents
- AI Content Generation
- AI Images
- AI Video
- AI Voice
- Scheduler
- Social Publishing
- Analytics
- Billing
- Team Workspace
- Admin Panel

---

# AI Instructions

When generating code:

- Follow existing project architecture.
- Never rewrite existing modules unless requested.
- Produce production-ready code.
- Use type hints.
- Keep code modular.
- Prefer clean architecture.
