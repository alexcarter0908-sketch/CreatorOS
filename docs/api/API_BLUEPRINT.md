# CreatorOS API Blueprint

# API Style

REST API

JSON Responses

JWT Authentication

Versioned

/api/v1/

---

# Authentication

POST /auth/register

POST /auth/login

POST /auth/logout

GET /auth/me

---

# Projects

GET /projects

POST /projects

GET /projects/{id}

PATCH /projects/{id}

DELETE /projects/{id}

---

# AI Jobs

POST /jobs

GET /jobs

GET /jobs/{id}

DELETE /jobs/{id}

---

# AI Generation

POST /generate/script

POST /generate/storyboard

POST /generate/image

POST /generate/video

POST /generate/voice

POST /generate/thumbnail

POST /generate/seo

---

# Publishing

POST /youtube/publish

POST /youtube/schedule

GET /youtube/channels

---

# Analytics

GET /analytics/dashboard

GET /analytics/project/{id}

---

# Billing

GET /billing

POST /billing/checkout

GET /billing/history