# CreatorOS Database Blueprint

# Goal

The database must support:

- Single users
- Teams
- Multi-channel management
- AI workflows
- Assets
- Publishing
- Analytics
- Billing

without major redesign.

---

# Core Entities

User

Workspace

Project

Channel

Script

Storyboard

Scene

Asset

Video

Thumbnail

SEO

Publish Job

Analytics

AI Job

Provider

API Key

Credit Wallet

Billing

Notification

Audit Log

---

# Relationships

User

↓

Workspace

↓

Projects

↓

Scripts

↓

Scenes

↓

Assets

↓

Videos

↓

Publishing

↓

Analytics

---

# Design Rules

UUID Primary Keys

Soft Deletes

Created At

Updated At

Status Fields

Indexes

Foreign Keys

Audit Logs

---

# AI Philosophy

CreatorOS stores workflow.

AI providers remain replaceable.

The database should never depend on a single AI provider.

---

# Future Ready

Teams

Roles

Permissions

Automation

Marketplace

API

Enterprise