---
{
  "id": "file_aswe2v04",
  "filetype": "document",
  "filename": "scp_foundation_archive_project_plan",
  "created_at": "2026-06-20T00:30:44.257Z",
  "updated_at": "2026-06-20T00:30:48.596Z",
  "meta": {
    "location": "/",
    "tags": [],
    "categories": [],
    "description": "",
    "source": "markdown"
  }
}
---
# 🏛️ SCP Foundation Archive — Project Plan

Here's the comprehensive plan for building an interactive SCP archive with an AI guide.

---

## 📋 Project Overview

**Stack**: React/Next.js (TypeScript) + Python FastAPI + SQLite → PostgreSQL later\
**Source**: [scp-wiki.wikidot.com](http://scp-wiki.wikidot.com) (all SCPs, tales, GOI formats)\
**AI**: Comprehensive assistant (lore chatbot + recommendations + smart search + narrative guide)\
**Deployment**: Local first, cloud later

---

## 🧱 Architecture

```
scp-archive/
├── scraper/              # Python - Wikidot scraper
│   ├── scp_scraper.py    # Main scraper engine
│   ├── wikidot_parser.py # Parse Wikidot syntax to markdown
│   ├── models.py         # Data models (SCP, Tale, GOI, Tag)
│   └── requirements.txt
├── backend/              # Python FastAPI
│   ├── main.py           # API server
│   ├── database.py       # SQLite/Postgres connection
│   ├── models.py         # SQLAlchemy models
│   ├── routes/
│   │   ├── scps.py       # SCP CRUD endpoints
│   │   ├── search.py     # Full-text + semantic search
│   │   ├── tags.py       # Tag/category endpoints
│   │   └── ai.py         # AI guide endpoints
│   └── ai/
│       ├── guide.py      # AI guide orchestration
│       ├── lore.py       # Lore context builder
│       └── recommend.py  # Recommendation engine
├── frontend/             # Next.js 14+ App Router
│   ├── app/
│   │   ├── page.tsx      # Landing / SCP browser
│   │   ├── scp/
│   │   │   └── [id]/
│   │   │       └── page.tsx  # Individual SCP viewer
│   │   ├── search/
│   │   │   └── page.tsx  # Advanced search
│   │   ├── tales/
│   │   │   └── page.tsx  # Tales browser
│   │   ├── goi/
│   │   │   └── page.tsx  # Groups of Interest
│   │   └── ai-guide/
│   │       └── page.tsx  # AI guide chat interface
│   ├── components/
│   │   ├── SCPCard.tsx
│   │   ├── SCPViewer.tsx
│   │   ├── SearchBar.tsx
│   │   ├── TagCloud.tsx
│   │   ├── AIChat.tsx
│   │   └── ...
│   └── lib/
│       ├── api.ts        # API client
│       └── types.ts      # TypeScript types
└── docker-compose.yml    # For easy local dev
```

---

## 📦 Phase 1: Scraper (Python)

Build a Wikidot scraper that:

- Crawls the SCP series pages (Series 1-9) to get all SCP URLs
- Crawls tale hubs, GOI format hubs
- Extracts: **title, object class, containment procedures, description, tags, author, rating, created date**
- Parses Wikidot syntax into clean Markdown/HTML
- Stores everything in a structured JSON/SQLite format
- Handles rate limiting (respect robots.txt, polite delays)

**Key data model per entry:**

```json
{
  "id": "SCP-173",
  "title": "The Sculpture",
  "object_class": "Euclid",
  "secondary_class": null,
  "containment_procedures": "...",
  "description": "...",
  "tags": ["scp", "euclid", "statue", "living", "hostile"],
  "author": "Moto42",
  "rating": 2842,
  "created_date": "2008-07-17",
  "type": "scp",  // or "tale", "goi-format"
  "related_scps": ["SCP-131", "SCP-682"],
  "content_html": "...",
  "content_md": "..."
}
```

---

## 📦 Phase 2: Backend API (Python FastAPI)

- **REST API** with endpoints:
  - `GET /api/scps` — paginated list with filters (class, tags, rating, series)
  - `GET /api/scps/{id}` — full SCP details
  - `GET /api/search?q=...` — full-text search across all content
  - `GET /api/tags` — tag cloud with counts
  - `GET /api/tales` — tales listing
  - `GET /api/goi` — GOI formats listing
  - `POST /api/ai/ask` — AI guide chat (sends context + question to LLM)
  - `POST /api/ai/recommend` — get recommendations based on an SCP
- **SQLite** database with full-text search (FTS5)
- **Vector embeddings** for semantic search (using sentence-transformers or OpenAI embeddings)

---

## 📦 Phase 3: Frontend (Next.js)

**Pages:**

1. **Home** — Featured SCPs, random SCP, stats dashboard, search bar
2. **SCP Browser** — Grid/list view with filters (class, tags, rating, series), infinite scroll
3. **SCP Detail** — Full article viewer with:
   - Object class badge with color coding
   - Containment procedures
   - Description (rendered from markdown)
   - Tags as clickable filters
   - Related SCPs
   - Rating, author info
   - "Ask the AI Guide" button
4. **Tales Browser** — Browse SCP Foundation tales
5. **GOI Browser** — Groups of Interest formats
6. **AI Guide** — Chat interface with:
   - Lore Q&A
   - SCP recommendations
   - Narrative/canon explanations
   - Smart search
7. **Advanced Search** — Multi-faceted search with filters

**Design Theme:** SCP Foundation aesthetic — dark mode, monospace/typewriter fonts, redacted text effects, containment cell feel, Foundation logo/branding

---

## 📦 Phase 4: AI Guide

The AI guide will be powered by your API key (Anthropic or OpenAI) and will:

- **Retrieve relevant context** from the database based on the user's question
- **Build a prompt** with SCP lore context + the question
- **Stream responses** for a chat-like experience
- **Support features:**
  - "Tell me about SCP-173"
  - "What SCPs are similar to SCP-682?"
  - "Explain the Church of the Broken God"
  - "Walk me through the Antimemetics Division canon"
  - "Find all Keter-class SCPs that are aquatic"

---

## 📅 Implementation Order

| Phase | What | Est. Time |
| --- | --- | --- |
| **1** | Scraper — build and run to populate database | \~2-3 hrs |
| **2** | Backend API — FastAPI with all endpoints | \~2-3 hrs |
| **3** | Frontend — Next.js app with all pages | \~4-5 hrs |
| **4** | AI Guide integration | \~2 hrs |
| **5** | Polish — design, UX, edge cases | \~1-2 hrs |

---

## 🎨 Visual Design Concept

The UI will be styled like an **SCP Foundation internal database terminal**:

- Dark backgrounds (#0a0a0a, #1a1a2e)
- Green/amber monospace text accents
- Object class badges with distinct colors (Safe=green, Euclid=yellow, Keter=red, Thaumiel=blue, etc.)
- "REDACTED" blur effects for classified content
- Typewriter-style animations
- Foundation logo and O5 Council branding

---

## ❓ Questions Before We Start

1. **API Provider**: Which LLM API do you want to use for the AI guide? (Anthropic Claude, OpenAI GPT, or both?)
2. **Project Name**: What should we call this project? (e.g., "SCP-Archive", "FoundationDB", "The Archive")
3. **Scraper Depth**: For tales and GOI formats, should we scrape ALL of them (potentially thousands) or focus on the most popular/connected ones first?

Once you confirm, we can toggle to **Act Mode** and start building!