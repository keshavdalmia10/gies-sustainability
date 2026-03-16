# Gies Sustainability Impact Dashboard

The Gies Sustainability Impact Dashboard is a multi-persona web application for turning scattered research activity into decision-ready sustainability insight.

It combines a React frontend, a FastAPI backend, PostgreSQL-backed analytics, AI-assisted matching workflows, and a production deployment on DigitalOcean. The product is designed for four main audiences:

- Leadership teams that need portfolio-level visibility.
- Donors and funders that need credible impact stories and funding opportunities.
- Students that need mentor and project discovery.
- Faculty and administrators that need collaboration, profile updates, and validation workflows.

## Why This Project Exists

Universities are usually strong at storing publications and weak at explaining why those publications matter operationally.

This project exists to solve five recurring problems:

- Research impact is hard to explain beyond publication counts.
- Donor conversations stall when there is no clear evidence trail from research to outcomes.
- Leadership teams struggle to compare departments, SDGs, and momentum in one place.
- Students often cannot find the right faculty, projects, or skills network quickly enough.
- Sustainability data is fragmented across publications, grants, patents, policy references, and manually maintained narratives.

The dashboard addresses that by giving each audience a focused decision surface while keeping the data model shared underneath.

## Product Summary

At a high level, the platform does six things:

- Aggregates faculty, publication, impact, and networking data into one application database.
- Presents role-specific dashboards instead of one generic research portal.
- Links published research to structured impact cards and supporting evidence.
- Exposes analytics endpoints for leadership reporting and portfolio review.
- Supports AI-assisted donor matching, project discovery, news summarization, and network analysis.
- Adds lightweight trust mechanisms such as validation, leaderboards, and visible evidence context.

## Feature Matrix

The table below is the quickest way to understand the product, the reason each feature exists, and the main tech used to deliver it.

| Area | Functionality | Why it exists | Main tech |
| --- | --- | --- | --- |
| Home page | Persona routing, trust framing, SDG news feed, before/after story | Helps a new user understand the product quickly and self-select into the right workflow | React, React Router, Lucide icons, NewsAPI fallback logic, OpenAI news insight generation |
| Dean view | Summary KPIs, publication trends, department comparison, SDG distribution, top faculty analysis | Gives leadership a compact strategic dashboard for allocation, hiring, and portfolio review | React, Recharts, FastAPI analytics endpoints, PostgreSQL aggregations |
| Donor view | Published impact card browsing, SDG filtering, funding gap visibility, evidence CTA | Makes fundraising more concrete by turning research into investable narratives | React, Axios, FastAPI impact-card endpoints, PostgreSQL impact-card storage |
| Impact card validation | Approve or reject impact evidence and award student points | Introduces a human verification loop so trust does not depend only on AI output | FastAPI, PostgreSQL, gamification endpoints |
| Student view | SDG filtering, mentor discovery UI, project-oriented search | Lowers the friction for students trying to find relevant faculty and work | React, local demo dataset, reusable mentor cards |
| Networking hub | Student profile creation, graph exploration, AI network assistant, donor/project matching, faculty updates | Moves the product from static reporting into active collaboration and opportunity discovery | React, FastAPI, NetworkX, LangGraph, OpenAI, PostgreSQL networking tables |
| Faculty API | Faculty listing, profile retrieval, updates, publication drill-down | Enables profile management and supports student, donor, and analytics workflows | FastAPI, SQLAlchemy, PostgreSQL |
| News feed | SDG news retrieval plus AI-generated research opportunity text | Keeps the platform connected to external sustainability signals instead of only internal data | FastAPI, httpx, NewsAPI, OpenAI |
| Production deployment | Containerized frontend and backend, managed database, App Platform routing | Makes the system accessible without local setup and gives it a repeatable deployment path | Docker, Nginx, DigitalOcean App Platform, DigitalOcean Managed PostgreSQL, DOCR |

## Feature Deep Dive

### 1. Home and Orientation

The landing page is not just marketing copy. It is a product router for different decision-makers.

What it does:

- Introduces the "From Papers to Proof" framing.
- Shows trust-building ideas such as source transparency, human validation, and explainable confidence.
- Routes users into Dean, Donor, and Student journeys.
- Displays an SDG news feed with AI-generated research opportunity commentary.

Why it exists:

- Multi-persona products fail when the first screen is generic.
- Users need a fast explanation of what this system is for before they trust any downstream analytics.
- External sustainability signals help the product feel current instead of static.

Tech used:

- [App.tsx](/Users/keshavdalmia/Documents/case_competition/frontend/src/App.tsx)
- [HomePage.tsx](/Users/keshavdalmia/Documents/case_competition/frontend/src/pages/HomePage.tsx)
- [NewsFeed.tsx](/Users/keshavdalmia/Documents/case_competition/frontend/src/components/news/NewsFeed.tsx)
- [news.py](/Users/keshavdalmia/Documents/case_competition/backend/app/routers/news.py)

### 2. Dean / Leadership Dashboard

The Dean workflow is the most analytics-heavy area of the app.

What it does:

- Pulls summary metrics such as publications, faculty, departments, and SDG coverage.
- Renders publication momentum over time.
- Compares departmental output and sustainability contribution.
- Shows SDG mix and faculty influence views.
- Normalizes inconsistent API payload shapes so the UI can tolerate backend shape variation.

Why it exists:

- Leadership decisions need comparability more than raw detail.
- Department heads and provost teams need to spot concentration, gaps, and trend direction quickly.
- The dashboard makes it easier to justify resource allocation with visible evidence instead of anecdote.

Tech used:

- [DeanInteractiveDashboard.tsx](/Users/keshavdalmia/Documents/case_competition/frontend/src/components/dean/DeanInteractiveDashboard.tsx)
- [analytics.py](/Users/keshavdalmia/Documents/case_competition/backend/app/routers/analytics.py)
- Recharts for bar, area, pie, and scatter visualizations
- Async SQLAlchemy queries for aggregation against PostgreSQL

### 3. Donor and Funder Experience

The donor workflow centers the impact card as the core funding object.

What it does:

- Lists published impact cards.
- Filters cards by SDG.
- Surfaces current funding and open funding gaps.
- Shows geography and key outcomes.
- Links to a more detailed evidence-story view.

Why it exists:

- Donors fund stories with traceable outcomes, not raw publication tables.
- Funding gap visibility helps move from passive browsing to action.
- A donor-friendly surface lets the same research data support advancement conversations without needing a custom report every time.

Tech used:

- [DonorView.tsx](/Users/keshavdalmia/Documents/case_competition/frontend/src/pages/DonorView.tsx)
- [impact_cards.py](/Users/keshavdalmia/Documents/case_competition/backend/app/routers/impact_cards.py)
- PostgreSQL-backed `impact_cards` records
- Axios client in [api.ts](/Users/keshavdalmia/Documents/case_competition/frontend/src/services/api.ts)

Implementation note:

- The donor listing page is live and database-backed.
- The detailed impact-card page in [ImpactCardDetail.tsx](/Users/keshavdalmia/Documents/case_competition/frontend/src/pages/ImpactCardDetail.tsx) is currently a UI preview built on mock data, even though the backend already exposes a detailed impact-card endpoint.

### 4. Student Discovery

The student-facing view is intentionally simpler than the networking hub.

What it does:

- Lets users filter mentors by SDG.
- Supports text search across faculty names and active project labels.
- Presents opportunities in a mentor-card format.

Why it exists:

- Students often need a lightweight browsing surface before they are ready for deeper network tooling.
- A direct mentor discovery experience reduces the intimidation of navigating a full research graph.

Tech used:

- [StudentView.tsx](/Users/keshavdalmia/Documents/case_competition/frontend/src/pages/StudentView.tsx)
- [MentorCard.tsx](/Users/keshavdalmia/Documents/case_competition/frontend/src/components/MentorCard.tsx)

Implementation note:

- The current student page uses a frontend mock mentor dataset rather than live API data.
- The more dynamic student and networking features live in the Networking hub and backend networking endpoints.

### 5. Networking and Collaboration Hub

The Networking page is where the project becomes an active matching system instead of only a reporting dashboard.

What it does:

- Creates student profiles with major, year, skills, interests, and bio.
- Stores and updates networking entities in PostgreSQL.
- Builds a graph of students, faculty, skills, and interests.
- Provides an AI assistant that analyzes relationship patterns and returns suggested connections plus graph data.
- Supports donor-side project matching and faculty-side updates.
- Displays a gamified leaderboard based on student impact points.

Why it exists:

- Research ecosystems are networks, not flat lists.
- Faculty discovery, donor matching, and student engagement all improve when skills and interests become first-class objects.
- The AI assistant adds a conversational way to explore the network without requiring every user to understand graph structures.

Tech used:

- [Networking.tsx](/Users/keshavdalmia/Documents/case_competition/frontend/src/pages/Networking.tsx)
- [ProfileUpload.tsx](/Users/keshavdalmia/Documents/case_competition/frontend/src/components/networking/ProfileUpload.tsx)
- [NetworkChatbot.tsx](/Users/keshavdalmia/Documents/case_competition/frontend/src/components/networking/NetworkChatbot.tsx)
- [NetworkGraph.tsx](/Users/keshavdalmia/Documents/case_competition/frontend/src/components/networking/NetworkGraph.tsx)
- [networking.py](/Users/keshavdalmia/Documents/case_competition/backend/app/routers/networking.py)
- [gamification.py](/Users/keshavdalmia/Documents/case_competition/backend/app/routers/gamification.py)
- NetworkX, LangGraph, LangChain OpenAI, OpenAI, react-force-graph-2d

### 6. AI-Assisted Donor Matching

There are two complementary donor discovery tools inside the networking hub.

What they do:

- `Find Funding` takes a project description and returns donor matches with rationale.
- `For Donors` takes a donor interest and returns faculty or project matches.

Why they exist:

- Funding search is often performed manually across disconnected foundation and grant sources.
- Donors also need a way to start from their thematic priorities and discover internal opportunities worth supporting.

Tech used:

- [DonorSearch.tsx](/Users/keshavdalmia/Documents/case_competition/frontend/src/components/networking/DonorSearch.tsx)
- [DonorPortal.tsx](/Users/keshavdalmia/Documents/case_competition/frontend/src/components/networking/DonorPortal.tsx)
- [donors.py](/Users/keshavdalmia/Documents/case_competition/backend/app/routers/donors.py)
- LangChain OpenAI with `gpt-4o`

Implementation note:

- These workflows depend on `OPENAI_API_KEY`.
- They are AI-assisted matching tools, not authoritative grant databases.

### 7. Validation and Gamification

The platform includes a lightweight quality-control loop.

What it does:

- Allows impact-card validation submissions.
- Awards points to students when validations are approved.
- Exposes a leaderboard of the most active contributors.

Why it exists:

- Systems like this need incentives for human review.
- Validation activity converts trust into a measurable behavior rather than an abstract promise.

Tech used:

- [impact_cards.py](/Users/keshavdalmia/Documents/case_competition/backend/app/routers/impact_cards.py)
- [gamification.py](/Users/keshavdalmia/Documents/case_competition/backend/app/routers/gamification.py)
- `students` table plus impact point fields

## Current Feature Status

This is important because not every surface is equally mature.

### Live and database-backed

- Home page news feed
- Dean analytics dashboard
- Donor impact-card listing
- Faculty CRUD and publication drill-down
- Student profile creation
- Networking graph generation
- AI network analysis
- Donor matching endpoints
- Leaderboard and validation point tracking

### Present in the UI but partially mocked or demo-oriented

- Student mentor browsing page
- Impact-card detail page preview

### Present in the data model or broader repo but not part of the lean production runtime

- Some extended research/ML ingestion modules
- Additional routers outside the runtime app
- Older Terraform infrastructure files under `infra/terraform`

## System Architecture

### Frontend

- Single-page React application with persona-specific routes.
- Vite-based build for local development.
- Nginx-served static build in production.

### Backend

- Lean FastAPI runtime in [runtime_app.py](/Users/keshavdalmia/Documents/case_competition/backend/app/runtime_app.py).
- Async PostgreSQL access through SQLAlchemy.
- Router-based API surface for analytics, donors, faculty, gamification, impact cards, networking, and news.

### Data Layer

- PostgreSQL is the source of truth for faculty, publications, impacts, cards, students, skills, and interests.
- Relationship tables model network links between people and topics.

### AI Layer

- OpenAI powers donor matching, article insight generation, and networking analysis responses.
- LangGraph and LangChain orchestrate parts of the networking assistant flow.
- NetworkX constructs graph structures for collaboration analysis.

### Deployment Layer

- Frontend and backend are containerized separately.
- DigitalOcean App Platform runs both services.
- DigitalOcean Managed PostgreSQL stores application data.
- DigitalOcean Container Registry stores deployment images.

## Data Model and Why It Matters

The database is structured around both research output and people/network data.

### Core research tables

- `faculty`: who the institution can activate, analyze, or feature.
- `publications`: the base record for research output and SDG alignment.
- `impacts`: downstream outcomes such as grants, patents, and policies.
- `impact_cards`: donor-friendly narratives and summary objects.
- `publication_impact_links`: the evidence layer between papers and outcomes.

Why these exist:

- They let the product move from "who published what" to "what changed because of the work."

### Funding and evidence specialization tables

- `grants`
- `patents`
- `policies`
- `faculty_impact_links`
- `ground_truth_set`
- `model_evaluations`
- `faculty_feedback`
- `audit_logs`

Why these exist:

- They support explainability, governance, and ML evaluation rather than just CRUD operations.

### Networking tables

- `students`
- `skills`
- `interests`
- `student_skills`
- `student_interests`
- `faculty_skills`
- `faculty_interests`

Why these exist:

- They make collaboration and matchmaking possible without flattening everyone into a single profile blob.

## API Surface

The production runtime currently mounts these main route families:

### Analytics

- `/api/v1/analytics/summary`
- `/api/v1/analytics/departments`
- `/api/v1/analytics/trends/publications`
- `/api/v1/analytics/faculty/top`
- `/api/v1/analytics/sdg/distribution`

### Impact cards

- `/api/v1/impact-cards/`
- `/api/v1/impact-cards/{card_id}`
- `/api/v1/impact-cards/{card_id}/publish`
- `/api/v1/impact-cards/{card_id}/validate`

### Faculty

- `/api/v1/faculty/`
- `/api/v1/faculty/{faculty_id}`
- `/api/v1/faculty/{faculty_id}/publications`

### Networking

- `/api/v1/networking/student`
- `/api/v1/networking/faculty/{person_uuid}/skills`
- `/api/v1/networking/graph`
- `/api/v1/networking/analyze`

### Donors

- `/api/v1/donors/search`
- `/api/v1/donors/find-projects`

### Gamification

- `/api/v1/gamification/leaderboard`

### News

- `/api/v1/news/sdg`

### Health and docs

- `/api/health`
- `/api/docs`

Implementation note:

- The runtime intentionally serves both `/api/v1/...` and `/v1/...` internally so DigitalOcean App Platform path stripping does not break the public API routes.

## Technology Stack and Why Each Choice Was Made

### Frontend stack

| Technology | Why it is used |
| --- | --- |
| React 18 | Good fit for multi-view dashboard UX and interactive stateful flows |
| TypeScript | Reduces UI/data-contract mistakes across several personas and API shapes |
| Vite | Fast local iteration and simple production build pipeline |
| React Router | Clean persona-based route structure |
| Axios | Small, predictable HTTP client for backend integration |
| Recharts | Fast way to deliver leadership charts without building a visualization layer from scratch |
| react-force-graph-2d | Handles the networking graph visualization use case directly |
| Lucide React | Lightweight icon system for a product with many role-specific visual cues |

### Backend stack

| Technology | Why it is used |
| --- | --- |
| FastAPI | Typed, async-friendly API framework with built-in docs |
| SQLAlchemy | Flexible ORM and query layer for analytics and CRUD workloads |
| asyncpg | Efficient async PostgreSQL driver for runtime requests |
| psycopg2-binary | Useful for sync workflows and database tooling |
| Pydantic | Request and response validation |
| httpx | Async external API calls, especially for news fetching |
| NetworkX | Graph construction for collaboration analysis |
| OpenAI | LLM-backed matching, summarization, and narrative support |
| LangChain / LangGraph | Higher-level orchestration for AI-assisted workflows |

### Infrastructure stack

| Technology | Why it is used |
| --- | --- |
| Docker | Consistent local and production packaging |
| Nginx | Low-overhead static frontend serving with SPA routing support |
| DigitalOcean App Platform | Simple managed runtime for two-service deployment |
| DigitalOcean Managed PostgreSQL | Reduces operational overhead while keeping SQL as the core data model |
| DigitalOcean Container Registry | Stores deployable frontend and backend images |

## Repository Structure

```text
.
|-- backend/
|   |-- app/
|   |   |-- routers/
|   |   |-- services/
|   |   |-- models.py
|   |   |-- models_networking.py
|   |   |-- runtime_app.py
|   |   `-- settings.py
|   |-- Dockerfile
|   `-- requirements-runtime.txt
|-- frontend/
|   |-- src/
|   |   |-- components/
|   |   |-- pages/
|   |   `-- services/
|   |-- Dockerfile
|   `-- frontend.nginx.conf
|-- infra/
|   |-- digitalocean/
|   |   `-- app.yaml
|   `-- terraform/
`-- README.md
```

## Local Development

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-runtime.txt
```

Create an `.env` based on [backend/.env.example](/Users/keshavdalmia/Documents/case_competition/backend/.env.example), then run:

```bash
uvicorn app.runtime_app:app --reload --host 127.0.0.1 --port 8000
```

### 2. Frontend

```bash
cd frontend
npm ci
npm run dev
```

The Vite dev server expects the backend at `http://localhost:8000` and proxies `/api` traffic there.

### 3. Production-style containers

Backend image:

```bash
docker build -t gies-backend ./backend
```

Frontend image:

```bash
docker build -t gies-frontend ./frontend
```

## Deployment

The repo now includes a DigitalOcean App Platform template at [app.yaml](/Users/keshavdalmia/Documents/case_competition/infra/digitalocean/app.yaml).

Deployment shape:

- Frontend container on App Platform
- Backend container on App Platform
- Managed PostgreSQL database
- `/` routed to frontend
- `/api` routed to backend

Important deployment detail:

- Images must be built for `linux/amd64` before being pushed to DigitalOcean App Platform. Apple Silicon local images will fail with `exec format error` on the platform.

## Production Notes

Current production behavior:

- Frontend is served by Nginx on port `8080`.
- Backend is served by Uvicorn on port `8080`.
- Health endpoint is exposed at `/api/health`.
- Swagger UI is exposed at `/api/docs`.

The current deployed environment was validated against:

- homepage response
- backend health response
- live `/api/v1/faculty/` data
- managed database row counts after import

## Known Gaps and Next Steps

- Wire the impact-card detail page to the live backend detail endpoint.
- Replace the student mentor mock dataset with API-backed search.
- Tighten donor matching with richer source data and stronger output validation.
- Add a clearer distinction between MVP runtime modules and longer-term ingestion/ML modules.
- Refresh older documentation files that still describe pre-runtime architecture.

## License

This repository currently references MIT-style badging in older docs, but the root project should only claim a license once a final license file is added explicitly.
