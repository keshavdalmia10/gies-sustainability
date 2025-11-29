# Gies Sustainability Impact Dashboard - MVP Architecture
## Pillar 2: From Data to Decisions (Actionable Insight Generation)

> **Our submission is anchored in Pillar 2: From Data to Decisions, with targeted data-engine and UX enhancements where they directly unlock better decision-making.**

---

## Executive Summary

This MVP architecture transforms the current Gies Sustainability Dashboard from a **publication tracker** into a **decision engine** for leadership, donors, and students. The system generates rich "impact cards" that link faculty research → outputs (grants, patents, policies) → real-world outcomes (jobs, communities, programs).

**Pilot Scope:** SDG7 (Clean Energy) with 10 validated impact cards, Precision@5 ≥ 0.85, and 2 donor briefings.

---

## 1. System Architecture Overview

```mermaid
graph TB
    subgraph "Data Ingestion Layer"
        A1[Illinois Experts API] --> DI[Data Integration Service]
        A2[NIH RePORTER API] --> DI
        A3[NSF Awards API] --> DI
        A4[USPTO PatentsView API] --> DI
        A5[State Agency PDFs/RSS] --> DI
        A6[data.csv] --> DI
    end
    
    subgraph "Data Processing & Storage"
        DI --> DB[(PostgreSQL<br/>Core Data)]
        DI --> VDB[(Pinecone/FAISS<br/>Vector DB)]
        DI --> CACHE[(Redis Cache)]
    end
    
    subgraph "AI/ML Pipeline"
        DB --> SDG[SDG Classification<br/>Service]
        VDB --> SDG
        SDG --> MATCH[Impact Matching<br/>Engine]
        MATCH --> EVAL[Quality Evaluation<br/>Precision@k]
    end
    
    subgraph "Impact Generation"
        MATCH --> IC[Impact Cards<br/>Generator]
        EVAL --> IC
        IC --> DB
    end
    
    subgraph "Decision Support"
        IC --> DS1[Dean/Provost View]
        IC --> DS2[Donor View]
        IC --> DS3[Student View]
    end
    
    subgraph "Governance & Feedback"
        DS1 --> FB[Feedback Loop]
        DS2 --> FB
        DS3 --> FB
        FB --> EVAL
        FB --> GOV[Governance Service<br/>Data Retention]
    end
    
    subgraph "Frontend"
        DS1 --> FE[React Dashboard]
        DS2 --> FE
        DS3 --> FE
    end
    
    style DI fill:#e1f5ff
    style MATCH fill:#fff4e1
    style IC fill:#ffe1f5
    style EVAL fill:#e1ffe1
    style FE fill:#f5f5f5
```

---

## 2. Core Components

### 2.1 Data Ingestion Layer

#### 2.1.1 External Data Sources

| Source | Type | Access Method | Update Frequency | Rate Limit | Purpose |
|--------|------|---------------|------------------|------------|---------|
| **NIH RePORTER** | Grants | REST API | Monthly | 500 req/min | Link faculty to funded research |
| **NSF Awards** | Grants | REST API | Monthly | No limit (CSV) | Federal grant data |
| **USPTO PatentsView** | Patents | API/CSV | Quarterly | 45 req/min | Innovation & commercialization |
| **State Agencies** | Policy docs | PDF/RSS | Quarterly | N/A | Policy impact documents |
| **Illinois Experts** | Faculty | API | Weekly | Existing | Faculty profiles (current) |
| **data.csv** | Publications | File | On-demand | N/A | Existing publication data |

#### 2.1.2 Data Integration Service

**Tech Stack:** Python 3.10+, FastAPI, Celery (async tasks), PostgreSQL

**Key Functions:**
```python
class DataIntegrationService:
    """
    Orchestrates data ingestion from multiple sources
    """
    
    async def ingest_nih_grants(self, faculty_names: List[str]) -> List[Grant]:
        """
        Fetch grants from NIH RePORTER API
        - Match by PI name + institution
        - Extract: title, abstract, amount, dates, org
        - Rate limiting: 500 req/min with exponential backoff
        """
        pass
    
    async def ingest_nsf_awards(self, faculty_names: List[str]) -> List[Grant]:
        """
        Fetch grants from NSF Awards Search
        - Filter by PI + University of Illinois
        - Extract: award ID, program, amount, keywords
        """
        pass
    
    async def ingest_uspto_patents(self, faculty_names: List[str]) -> List[Patent]:
        """
        Fetch patents from USPTO PatentsView
        - Match by inventor name + assignee institution
        - Extract: patent #, title, abstract, classification, citations
        """
        pass
    
    async def ingest_state_policies(self, keywords: List[str]) -> List[PolicyDoc]:
        """
        Scrape/parse state agency documents
        - Illinois EPA, DCEO, OECD reports
        - Text extraction (PyPDF2, pdfplumber)
        - NER for University mentions
        """
        pass
```

**Data Validation:**
- Deduplication by DOI, grant #, patent #
- Name disambiguation (faculty matching)
- Completeness checks (required fields)
- Data quality scores

---

### 2.2 Database Schema

#### PostgreSQL (Core Relational Data)

```sql
-- Faculty table (existing + enhanced)
CREATE TABLE faculty (
    person_uuid UUID PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    department VARCHAR(255),
    active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Publications table (from data.csv + enhanced)
CREATE TABLE publications (
    article_uuid UUID PRIMARY KEY,
    person_uuid UUID REFERENCES faculty(person_uuid),
    title TEXT,
    abstract TEXT,
    publication_year INT,
    doi VARCHAR(255),
    journal_title VARCHAR(255),
    is_sustain BOOLEAN,
    sdg_top1 INT,
    sdg_top2 INT,
    sdg_top3 INT,
    sdg_confidence FLOAT,
    created_at TIMESTAMP
);

-- **NEW: Impact Entities**
CREATE TABLE impacts (
    impact_id UUID PRIMARY KEY,
    impact_type VARCHAR(50), -- 'grant', 'patent', 'policy', 'program'
    title TEXT,
    description TEXT,
    sdg_primary INT,
    sdg_secondary INT[],
    geography VARCHAR(255), -- 'Illinois', 'USA', 'Global'
    beneficiaries_count INT,
    funding_amount DECIMAL(15,2),
    status VARCHAR(50), -- 'active', 'completed', 'pending'
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Grants (subtype of impacts)
CREATE TABLE grants (
    grant_id UUID PRIMARY KEY REFERENCES impacts(impact_id),
    funder VARCHAR(255), -- 'NIH', 'NSF', 'DOE'
    program VARCHAR(255),
    pi_uuid UUID REFERENCES faculty(person_uuid),
    co_investigators UUID[],
    keywords TEXT[]
);

-- Patents (subtype of impacts)
CREATE TABLE patents (
    patent_id UUID PRIMARY KEY REFERENCES impacts(impact_id),
    patent_number VARCHAR(50),
    inventors UUID[], -- references faculty
    assignee VARCHAR(255),
    classification_codes VARCHAR(50)[],
    citations_count INT
);

-- Policy documents
CREATE TABLE policies (
    policy_id UUID PRIMARY KEY REFERENCES impacts(impact_id),
    agency VARCHAR(255),
    document_url TEXT,
    mention_type VARCHAR(50) -- 'research_cited', 'collaboration', 'expert_testimony'
);

-- **NEW: Impact Linkages**
CREATE TABLE publication_impact_links (
    link_id UUID PRIMARY KEY,
    publication_uuid UUID REFERENCES publications(article_uuid),
    impact_id UUID REFERENCES impacts(impact_id),
    confidence_score FLOAT, -- 0.0 - 1.0
    method VARCHAR(100), -- 'embedding_similarity', 'keyword_match', 'manual_validation'
    created_at TIMESTAMP
);

CREATE TABLE faculty_impact_links (
    link_id UUID PRIMARY KEY,
    person_uuid UUID REFERENCES faculty(person_uuid),
    impact_id UUID REFERENCES impacts(impact_id),
    role VARCHAR(100), -- 'PI', 'co-PI', 'inventor', 'expert'
    created_at TIMESTAMP
);

-- **NEW: Ground Truth & Evaluation**
CREATE TABLE ground_truth_set (
    gt_id UUID PRIMARY KEY,
    publication_uuid UUID REFERENCES publications(article_uuid),
    impact_id UUID REFERENCES impacts(impact_id),
    is_true_link BOOLEAN,
    sdg INT,
    validated_by VARCHAR(255),
    validated_at TIMESTAMP,
    notes TEXT
);

CREATE TABLE model_evaluations (
    eval_id UUID PRIMARY KEY,
    model_version VARCHAR(100),
    sdg INT,
    precision_at_k FLOAT,
    recall_at_k FLOAT,
    k INT,
    evaluation_date TIMESTAMP,
    notes TEXT
);

-- **NEW: Governance & Feedback**
CREATE TABLE faculty_feedback (
    feedback_id UUID PRIMARY KEY,
    person_uuid UUID REFERENCES faculty(person_uuid),
    feedback_type VARCHAR(50), -- 'correction', 'opt_out', 'add_impact'
    entity_type VARCHAR(50), -- 'publication', 'impact', 'link'
    entity_id UUID,
    comments TEXT,
    status VARCHAR(50), -- 'pending', 'resolved', 'rejected'
    created_at TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE TABLE data_retention_policies (
    policy_id UUID PRIMARY KEY,
    entity_type VARCHAR(50), -- 'logs', 'feedback', 'evaluations'
    retention_days INT,
    last_purge_date DATE
);

-- **NEW: Impact Cards**
CREATE TABLE impact_cards (
    card_id UUID PRIMARY KEY,
    person_uuid UUID REFERENCES faculty(person_uuid),
    sdg INT,
    title VARCHAR(500),
    summary TEXT,
    publications UUID[],
    impacts UUID[],
    key_outcomes TEXT[], -- ['200 jobs created', '50MW solar capacity']
    geography VARCHAR(255),
    total_funding DECIMAL(15,2),
    status VARCHAR(50), -- 'draft', 'validated', 'published'
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### Vector Database (Pinecone / FAISS)

**Purpose:** Semantic search and similarity matching

```python
# Vector index structure
vector_index = {
    "publication_embeddings": {
        "id": "article_uuid",
        "vector": [float],  # 768-dim from sentence-transformers
        "metadata": {
            "title": str,
            "abstract": str,
            "sdg_top1": int,
            "year": int
        }
    },
    "impact_embeddings": {
        "id": "impact_id",
        "vector": [float],
        "metadata": {
            "type": str,  # 'grant', 'patent', 'policy'
            "title": str,
            "description": str
        }
    },
    "sdg_description_embeddings": {
        "id": "sdg_id",
        "vector": [float],
        "metadata": {
            "sdg_number": int,
            "sdg_title": str
        }
    }
}
```

---

### 2.3 AI/ML Pipeline

#### 2.3.1 SDG Classification Service

**Tech Stack:** Python, Transformers, Pinecone

```python
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

class SDGClassifier:
    """
    Two-stage AI-powered SDG classification
    """
    
    def __init__(self):
        self.model = SentenceTransformer('all-mpnet-base-v2')  # 768-dim embeddings
        self.sdg_descriptions = self._load_sdg_descriptions()
    
    def classify_sustainability_relevance(self, text: str) -> Tuple[bool, float]:
        """
        Stage 1: Binary sustainability classification
        Returns: (is_sustainable, confidence_score)
        """
        # Use GPT-4/Claude for binary classification
        # Prompt: "Is this research relevant to UN SDGs? Yes/No"
        pass
    
    def identify_sdg_goals(self, text: str, top_k: int = 3) -> List[Tuple[int, float]]:
        """
        Stage 2: Identify top-K SDG goals using vector similarity
        Returns: [(sdg_number, similarity_score), ...]
        """
        text_embedding = self.model.encode(text)
        
        # FAISS similarity search against SDG descriptions
        similarities = self._vector_search(text_embedding, top_k=top_k)
        
        return similarities
```

#### 2.3.2 Impact Matching Engine

**Core Algorithm:** Multi-modal matching using embeddings + metadata

```python
class ImpactMatcher:
    """
    Links publications to impacts (grants, patents, policies)
    """
    
    def match_publication_to_impacts(
        self,
        publication_uuid: str,
        candidate_impacts: List[str],
        threshold: float = 0.75
    ) -> List[Tuple[str, float]]:
        """
        Match publication to related impacts using:
        1. Embedding similarity (title + abstract)
        2. Keyword overlap (SDG, terms)
        3. Temporal proximity (publication year vs grant/patent dates)
        4. Author matching (faculty links)
        
        Returns: [(impact_id, confidence_score), ...]
        """
        
        # Fetch publication embedding
        pub_embedding = self._get_embedding(publication_uuid, type='publication')
        
        matches = []
        for impact_id in candidate_impacts:
            impact_embedding = self._get_embedding(impact_id, type='impact')
            
            # Cosine similarity
            semantic_score = cosine_similarity(pub_embedding, impact_embedding)
            
            # Metadata signals
            keyword_score = self._keyword_overlap(publication_uuid, impact_id)
            temporal_score = self._temporal_proximity(publication_uuid, impact_id)
            author_score = self._author_match(publication_uuid, impact_id)
            
            # Weighted combination
            final_score = (
                0.5 * semantic_score +
                0.2 * keyword_score +
                0.15 * temporal_score +
                0.15 * author_score
            )
            
            if final_score >= threshold:
                matches.append((impact_id, final_score))
        
        return sorted(matches, key=lambda x: x[1], reverse=True)
```

#### 2.3.3 Quality Evaluation - Precision@k

**Ground Truthing Plan:**

1. **Manual Selection:** Pick 10-20 SDG7 faculty-impact cases with known relationships
2. **Human Validation:** Subject matter experts label:
   - True SDG classification
   - True publication ↔ grant/patent/policy links
3. **Metrics:**
   - **Precision@k:** Of the top k predictions, what % are correct?
   - **Recall@k:** Of all true links, what % are in the top k?

```python
class ModelEvaluator:
    """
    Evaluate matching quality using Precision@k
    """
    
    def compute_precision_at_k(
        self,
        predictions: List[Tuple[str, float]],  # (impact_id, score)
        ground_truth: List[str],  # true impact_ids
        k: int = 5
    ) -> float:
        """
        Precision@k = |{relevant} ∩ {top k}| / k
        """
        top_k_ids = [pred[0] for pred in predictions[:k]]
        relevant_in_top_k = set(top_k_ids) & set(ground_truth)
        
        return len(relevant_in_top_k) / k
    
    def evaluate_sdg7_pilot(self) -> Dict:
        """
        Run full evaluation on SDG7 ground truth set
        Target: Precision@5 ≥ 0.85
        """
        gt_cases = self._load_ground_truth_set(sdg=7)
        
        results = []
        for case in gt_cases:
            predictions = self.matcher.match_publication_to_impacts(
                case['publication_uuid'],
                case['candidate_impacts']
            )
            
            p_at_3 = self.compute_precision_at_k(predictions, case['true_impacts'], k=3)
            p_at_5 = self.compute_precision_at_k(predictions, case['true_impacts'], k=5)
            
            results.append({
                'case_id': case['id'],
                'precision_at_3': p_at_3,
                'precision_at_5': p_at_5
            })
        
        avg_p5 = np.mean([r['precision_at_5'] for r in results])
        
        return {
            'average_precision_at_5': avg_p5,
            'target_met': avg_p5 >= 0.85,
            'detailed_results': results
        }
```

---

### 2.4 Impact Card Generator

**Purpose:** Create rich, decision-ready impact narratives

```python
from dataclasses import dataclass
from typing import List

@dataclass
class ImpactCard:
    """
    Single faculty impact card for a specific SDG
    """
    faculty_name: str
    faculty_department: str
    sdg_number: int
    sdg_title: str
    
    # Story
    summary: str  # 2-3 sentence narrative
    key_outcomes: List[str]  # ['200 jobs created', '50MW solar financed']
    
    # Evidence
    publications: List[dict]  # {title, year, journal, doi}
    grants: List[dict]  # {funder, amount, title, years}
    patents: List[dict]  # {number, title, year}
    policies: List[dict]  # {agency, document, mention_type}
    
    # Metrics
    total_funding: float
    communities_reached: int
    geography: str  # 'Illinois', 'Midwest', 'Global'
    
    # Timeline
    start_year: int
    end_year: int
    status: str  # 'ongoing', 'completed'
    
    # Donor info
    funding_gap: float  # For donor view
    next_milestones: List[str]


class ImpactCardGenerator:
    """
    Generate impact cards from linked data
    """
    
    def generate_card(self, faculty_uuid: str, sdg: int) -> ImpactCard:
        """
        Assemble all linked publications + impacts for one faculty + SDG
        """
        # Fetch faculty info
        faculty = self._get_faculty(faculty_uuid)
        
        # Get SDG-relevant publications
        publications = self._get_publications(faculty_uuid, sdg=sdg)
        
        # Get linked impacts
        grants = self._get_linked_grants(publications)
        patents = self._get_linked_patents(publications)
        policies = self._get_linked_policies(publications)
        
        # Extract outcomes
        key_outcomes = self._extract_outcomes(grants, patents, policies)
        
        # Generate narrative summary using LLM
        summary = self._generate_summary(
            faculty, publications, grants, patents, policies, sdg
        )
        
        return ImpactCard(
            faculty_name=faculty.name,
            faculty_department=faculty.department,
            sdg_number=sdg,
            sdg_title=SDG_TITLES[sdg],
            summary=summary,
            key_outcomes=key_outcomes,
            publications=publications,
            grants=grants,
            patents=patents,
            policies=policies,
            total_funding=sum(g['amount'] for g in grants),
            # ... other fields
        )
    
    def _generate_summary(self, faculty, pubs, grants, patents, policies, sdg) -> str:
        """
        Use GPT-4 to generate compelling 2-3 sentence narrative
        
        Prompt template:
        "Professor {name} develops {research area} innovation (SDG{sdg}) that leads to
        {outcome}. Within {timeframe}, this work has {impact metrics}."
        """
        pass
```

---

### 2.5 Decision-Focused Frontend

#### 2.5.1 Persona-Based Entry Points

**Landing Page:**

```
┌─────────────────────────────────────────────────────┐
│  Gies Sustainability Impact Dashboard               │
│  "Turning Research into Real-World Change"          │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Featured Impact Story:                             │
│  ┌──────────────────────────────────────────────┐  │
│  │ Professor X develops solar financing         │  │
│  │ innovation (SDG7) → 200 rooftop systems →    │  │
│  │ 200+ local jobs in Illinois cooperatives     │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │  Dean/   │  │  Donor   │  │ Student  │         │
│  │ Leader   │  │ "Fund    │  │ "Find My │         │
│  │ "Invest" │  │  Impact" │  │ Mentor"  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────┘
```

#### 2.5.2 Dean/Provost View - "Strategic Gaps & Bets"

**Purpose:** Where should we invest next?

**Visualizations:**

1. **SDG × Department Matrix**
   - Heatmap: cells colored by (impact score × growth rate)
   - Labels: "Rising", "Mature", "Nascent"

2. **Momentum Indicators**
   - Publication growth rate (5-year trend)
   - Grant capture rate ($ per faculty)
   - External collaboration growth

3. **Gap Analysis**
   - SDGs with societal importance but low internal activity
   - Peer comparison (similar universities)

**Tech:** React + D3.js + Material-UI

#### 2.5.3 Donor View - "Fund This Impact"

**Purpose:** Which projects should I fund?

**Features:**

1. **Filterable Impact Cards**
   - Filter by: SDG, region (Illinois/Midwest/Global), outcome type (jobs/policy/startups)
   - Sort by: funding gap, community reach, innovation potential

2. **Card Design (Mini One-Pager)**
   ```
   ┌────────────────────────────────────────┐
   │ SDG 7: Clean Energy                    │
   │ Prof. Jane Doe | Finance Department    │
   ├────────────────────────────────────────┤
   │ Solar financing for rural cooperatives │
   │                                         │
   │ ✓ 3 publications in top journals       │
   │ ✓ $2.1M NIH/DOE grants                 │
   │ ✓ 2 patents (community solar models)   │
   │ ✓ IL EPA policy adoption (2023)        │
   │                                         │
   │ Real-World Impact:                     │
   │ • 200 solar installations              │
   │ • 15 IL communities reached            │
   │ • 200+ jobs created                    │
   │                                         │
   │ Next Milestone:                        │
   │ Scale to 10 Midwest states             │
   │ Funding Gap: $500K                     │
   │                                         │
   │ [Fund This Opportunity →]              │
   └────────────────────────────────────────┘
   ```

3. **CTA:** Link to Gies Advancement Office contact form

#### 2.5.4 Student View - "Find My Mentor"

**Purpose:** Who should I work with?

**Flow:**
1. **Interest Selection:** "I'm interested in SDG ___ + keyword ___"
2. **Faculty Cards:**
   - Photo, name, department
   - Recent SDG projects
   - Active grants/labs
   - Student opportunities (RA roles, competitions, courses)
3. **Contact:** Email link + calendar integration

---

### 2.6 Governance & Feedback

#### 2.6.1 Governance Model

**Ownership:**
- **Primary:** CPRBS (Center for Professional Responsibility in Business and Society)
- **Technical:** Gies Analytics Team
- **Advisory:** Faculty committee (1 rep per department)

**Data Retention:**
- **Derived analytics:** Indefinite (with annual refresh)
- **Source data:** Yearly refresh cycle
- **Logs:** 2-year rolling window (auto-purge)
- **Feedback/corrections:** Permanent

**Access Control:**
- **Public:** Impact cards, SDG summaries
- **Internal:** Detailed analytics, evaluation metrics, admin feedback

#### 2.6.2 Faculty Feedback Loop

**Mechanism:**

1. **Review Link:** Each impact card has "Suggest a Change" button
2. **Feedback Types:**
   - Correction (wrong SDG, wrong link)
   - Add Impact (missing grant/patent)
   - Opt-out (privacy request)
3. **Workflow:**
   - Faculty submits → Admin reviews → System updates
   - Corrections feed back into model retraining

**UI Component:**

```jsx
// Feedback form
<FeedbackForm>
  <Select label="Issue Type">
    <option>Wrong SDG Classification</option>
    <option>Missing Grant/Patent</option>
    <option>Incorrect Link</option>
    <option>Privacy/Opt-out Request</option>
  </Select>
  <TextArea label="Details" />
  <Button>Submit Feedback</Button>
</FeedbackForm>
```

---

## 3. Implementation Phases

### Phase 1: Foundation (Weeks 1-4)

1. **Database Setup**
   - PostgreSQL schema creation
   - Pinecone/FAISS index setup
   - Data migration from data.csv

2. **Data Ingestion - Core**
   - NIH RePORTER integration
   - NSF Awards integration
   - Faculty name disambiguation

3. **SDG Classification**
   - Load existing SDG classifications from data.csv
   - Implement Stage 1 (binary) + Stage 2 (top-K)

### Phase 2: Impact Linking (Weeks 5-8)

1. **Impact Matching Engine**
   - Embedding-based similarity
   - Metadata matching (keywords, authors, dates)
   - Confidence scoring

2. **Ground Truth Creation**
   - Select 10-20 SDG7 cases
   - Manual validation by domain experts
   - Store in ground_truth_set table

3. **Evaluation Framework**
   - Precision@k calculator
   - Target: P@5 ≥ 0.85

### Phase 3: Impact Cards  (Weeks 9-12)

1. **Card Generation**
   - Implement ImpactCardGenerator
   - LLM-based narrative summaries
   - Outcome extraction

2. **10 Validated Cards**
   - Generate for SDG7 faculty
   - Human review + corrections
   - Publish to card repository

3. **USPTO & Policy Integration**
   - Patent API integration
   - IL EPA/DCEO document scraping

### Phase 4: Frontend & UX (Weeks 13-16)

1. **Persona Views**
   - Dean/Provost dashboard (Strategic Gaps)
   - Donor view (Impact Cards)
   - Student view (Find My Mentor)

2. **Visualizations**
   - D3.js SDG matrix
   - Trend charts
   - Network graphs (faculty collaborations)

3. **Feedback System**
   - Faculty correction forms
   - Admin review workflow

### Phase 5: Pilot & Refinement (Weeks 17-20)

1. **2 Donor Briefings**
   - Create PowerPoint decks using impact cards
   - Present to 2 prospective donors (SDG7 focus)
   - Collect feedback

2. **Model Tuning**
   - Adjust matching thresholds based on feedback
   - Retrain if P@5 < 0.85

3. **Documentation**
   - User guides
   - API documentation
   - Governance policies

---

## 4. Technical Implementation Details

### 4.1 Tech Stack Summary

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.10+, FastAPI |
| **Database** | PostgreSQL 15 |
| **Vector DB** | Pinecone (cloud) or FAISS (local) |
| **Cache** | Redis |
| **Task Queue** | Celery + RabbitMQ |
| **ML/AI** | Transformers, Sentence-Transformers, OpenAI API |
| **Frontend** | React 18, TypeScript, Material-UI |
| **Visualization** | D3.js, Recharts |
| **Hosting** | AWS (EC2, RDS, S3) or local |

### 4.2 API Structure

**FastAPI Backend:**

```python
from fastapi import FastAPI, Depends
from typing import List

app = FastAPI(title="Gies Sustainability Impact API")

# Faculty endpoints
@app.get("/api/v1/faculty/{faculty_id}")
async def get_faculty(faculty_id: str):
    """Get faculty profile"""
    pass

@app.get("/api/v1/faculty/{faculty_id}/publications")
async def get_faculty_publications(faculty_id: str, sdg: int = None):
    """Get publications, optionally filtered by SDG"""
    pass

# Impact endpoints
@app.get("/api/v1/impacts/{impact_id}")
async def get_impact(impact_id: str):
    """Get impact details (grant/patent/policy)"""
    pass

@app.post("/api/v1/impacts/match")
async def match_publication_to_impacts(
    publication_id: str,
    threshold: float = 0.75
):
    """Find related impacts for a publication"""
    pass

# Impact Cards
@app.get("/api/v1/impact-cards")
async def list_impact_cards(sdg: int = None, department: str = None):
    """List all impact cards with filters"""
    pass

@app.get("/api/v1/impact-cards/{card_id}")
async def get_impact_card(card_id: str):
    """Get full impact card"""
    pass

# Decision views
@app.get("/api/v1/decision-support/dean")
async def dean_dashboard_data():
    """Strategic gaps & bets data"""
    pass

@app.get("/api/v1/decision-support/donor")
async def donor_view_data(sdg: int = None):
    """Fundable impact cards"""
    pass

# Evaluation
@app.get("/api/v1/evaluation/metrics")
async def get_evaluation_metrics(sdg: int = None):
    """Precision@k and model performance"""
    pass

# Feedback
@app.post("/api/v1/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Faculty submit corrections"""
    pass
```

### 4.3 Frontend Structure

**React Component Hierarchy:**

```
src/
├── components/
│   ├── common/
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── SDGBadge.tsx
│   ├── dean/
│   │   ├── StrategicGapsMatrix.tsx
│   │   ├── MomentumChart.tsx
│   │   └── GapAnalysis.tsx
│   ├── donor/
│   │   ├── ImpactCardList.tsx
│   │   ├── ImpactCardDetail.tsx
│   │   └── FundingCTA.tsx
│   ├── student/
│   │   ├── FacultySearch.tsx
│   │   ├── FacultyCard.tsx
│   │   └── OpportunitiesList.tsx
│   └── feedback/
│       └── FeedbackForm.tsx
├── views/
│   ├── LandingPage.tsx
│   ├── DeanDashboard.tsx
│   ├── DonorView.tsx
│   └── StudentView.tsx
├── hooks/
│   ├── useFacultyData.ts
│   ├── useImpactCards.ts
│   └── useEvaluation.ts
├── services/
│   └── api.ts
└── App.tsx
```

---

## 5. How This Satisfies the Requirements

### ✅ Pillar 2: From Data to Decisions

**Decision Case 1 - Dean/Provost:**
- **Decision:** Where to invest in sustainability research?
- **Data Provided:** SDG momentum, gaps, flagship impact cards
- **Tool:** Strategic Gaps & Bets matrix

**Decision Case 2 - Donor:**
- **Decision:** Which projects to fund?
- **Data Provided:** 10 validated SDG7 impact cards, outcomes, funding gaps
- **Tool:** Filterable impact cards with "Fund This" CTA

**Decision Case 3 - Student:**
- **Decision:** Who to work with?
- **Data Provided:** Faculty profiles, active projects, opportunities
- **Tool:** Find My Mentor search

### ✅ Clear Data Pathway

- **NIH/NSF:** Grants ($ amounts, keywords)
- **USPTO:** Patents (innovation metrics)
- **State agencies:** Policy docs (real-world adoption)
- **Access methods:** REST APIs with rate limiting
- **Update frequencies:** Specified per source

### ✅ Ground-Truthing & Precision@k ≥ 0.85

- **Ground Truth Set:** 10-20 SDG7 cases, manually validated
- **Metric:** Precision@5 (of top 5 predictions, ≥85% correct)
- **Improvement Loop:** Tune thresholds, retrain models if needed

### ✅ Governance & Data Retention

- **Ownership:** CPRBS + Gies Analytics
- **Retention:** Derived data (indefinite), logs (2 years), source (yearly refresh)
- **Faculty Feedback:** "Suggest a Change" link → admin review → system update
- **Access Control:** Public (cards) vs Internal (diagnostics)

### ✅ Named Example to Humanize

- **Landing Page:** Professor X solar financing story
- **Impact Card:** Same professor as first example
- **Evaluation:** Same case in ground truth set
- **Donor Briefing:** Lead with this story

### ✅ Tightened Ask

**Request:**
> "Approve a 6-12 month SDG7 pilot that delivers:
> - 10 fully validated SDG7 impact cards
> - Recommendation engine reaching Precision@5 ≥ 0.85
> - 2 donor briefings using these impact cards"

---

## 6. API Keys & Configuration Needed

### External APIs

1. **NIH RePORTER:**
   - No API key required (public)
   - Rate limit: 500 requests/min
   - Docs: https://api.reporter.nih.gov/

2. **NSF Awards:**
   - No API key required (public CSV)
   - Docs: https://www.nsf.gov/awardsearch/

3. **USPTO PatentsView:**
   - No API key required (public)
   - Rate limit: 45 requests/min
   - Docs: https://patentsview.org/apis/api-endpoints

4. **OpenAI API (for LLM summaries):**
   - **Required:** API key
   - Model: GPT-4 or GPT-3.5-turbo
   - Cost: ~$0.03/1K tokens

5. **Pinecone (Vector DB):**
   - **Required:** API key
   - Free tier: 1 index, 100K vectors
   - Alternative: Use FAISS locally (no key)

### Configuration Template

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/gies_sustainability

# Vector DB
VECTOR_DB=pinecone  # or 'faiss'
PINECONE_API_KEY=your_key_here
PINECONE_ENVIRONMENT=us-west1-gcp

# AI/ML
OPENAI_API_KEY=your_key_here
EMBEDDING_MODEL=all-mpnet-base-v2

# External APIs
NIH_API_BASE=https://api.reporter.nih.gov/v2
NSF_API_BASE=https://www.nsf.gov/awardsearch/
USPTO_API_BASE=https://api.patentsview.org/patents/query

# Cache
REDIS_URL=redis://localhost:6379/0

# Task Queue
CELERY_BROKER_URL=amqp://localhost

# Frontend
REACT_APP_API_BASE=http://localhost:8000/api/v1
```

---

## 7. Next Steps

1. **Review & Approve Architecture:** Stakeholder sign-off
2. **Set up Development Environment:** Install dependencies, databases
3. **Create Project Repository:** GitHub with structured folders
4. **Assign Tasks:** Map phases to team members
5. **Weekly Standups:** Track progress against 20-week timeline

---

## 8. Deliverables Summary

| Deliverable | Description | Timeline |
|-------------|-------------|----------|
| **Database Schema** | PostgreSQL + Vector DB setup | Week 4 |
| **Data Ingestion Pipeline** | NIH, NSF, USPTO, IL agencies | Week 8 |
| **Impact Matching Engine** | Embedding + metadata matching | Week 10 |
| **10 Validated Impact Cards** | SDG7 faculty cards, human-reviewed | Week 12 |
| **Precision@5 ≥ 0.85** | Evaluation metrics on ground truth | Week 12 |
| **Dean/Donor/Student Views** | React dashboards | Week 16 |
| **2 Donor Briefings** | PowerPoint + in-person presentations | Week 18 |
| **Documentation** | User guides, API docs, governance | Week 20 |

---

## Appendix A: Sample Impact Card (SDG7)

### Professor Jane Doe | Finance Department
**SDG 7: Affordable and Clean Energy**

**Summary:**
Professor Doe develops innovative solar financing models that enable rural electric cooperatives to fund distributed solar installations. Her research, published in top finance journals, led to a $2.1M DOE grant and partnerships with 15 Illinois communities. Within 3 years, this work has financed 200 rooftop solar systems, creating 200+ local jobs and avoiding 5,000 tons of CO₂ emissions annually.

**Evidence:**

*Publications:*
- "Community Solar Financing: A Cooperative Model" (2020, Journal of Finance) - 45 citations
- "Risk Pooling in Renewable Energy Investments" (2021, Energy Economics)
- "Behavioral Finance and Green Energy Adoption" (2022, Review of Financial Studies)

*Grants:*
- DOE Clean Energy Financing Initiative: $2.1M (2019-2023)
- NSF EAGER: Rural Energy Transitions: $150K (2020-2021)

*Patents:*
- US Patent #10,234,567: "Solar Financing Risk Assessment System" (2021)
- Patent Pending: "Cooperative Energy Investment Platform" (2023)

*Policy Impact:*
- Illinois EPA Clean Energy Plan (2023): Cites Doe's research as model for statewide cooperative solar program
- USDA Rural Development: Adopted financing guidelines based on Doe's cooperative model (2022)

**Real-World Outcomes:**
- 🏘️ **Communities:** 15 Illinois rural cooperatives
- ☀️ **Solar Capacity:** 10 MW distributed solar installed
- 💼 **Jobs:** 200+ installation, maintenance, and admin jobs
- 🌍 **Environmental:** 5,000 tons CO₂ avoided/year
- 💰 **Funding Leveraged:** $8M in private investment

**Next Milestone:**
Scale cooperative solar model to 10 Midwest states, targeting 100 additional cooperatives and 50 MW capacity.

**Funding Gap:** $500K for technology platform + pilot expansion

---

[Fund This Opportunity →] [Contact Prof. Doe] [Download Full Report]

---

## Appendix B: Data Flow Diagram

```mermaid
sequenceDiagram
    participant User as User (Dean/Donor/Student)
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant DB as PostgreSQL
    participant VDB as Vector DB (Pinecone)
    participant EXT as External APIs<br/>(NIH, NSF, USPTO)
    participant ML as ML Pipeline<br/>(SDG, Matching)
    
    User->>FE: Visit dashboard
    FE->>API: GET /impact-cards?sdg=7
    API->>DB: Query impact_cards table
    DB-->>API: Return cards
    API-->>FE: JSON response
    FE->>User: Display impact cards
    
    Note over API,EXT: Background: Daily Data Ingestion
    API->>EXT: Fetch new grants (NIH)
    EXT-->>API: Grant data
    API->>ML: Classify SDG
    ML->>VDB: Generate embeddings
    VDB-->>ML: Store vectors
    ML->>API: SDG classification
    API->>DB: Insert grants + links
    
    Note over User,API: Faculty Feedback Loop
    User->>FE: Submit correction
    FE->>API: POST /feedback
    API->>DB: Store feedback
    DB-->>API: OK
    API->>ML: Retrain with correction
    ML-->>API: Updated model
```

---

This architecture provides a **complete, implementable blueprint** for the MVP that satisfies all Pillar 2 requirements. It integrates external data sources, implements rigorous evaluation (Precision@k), creates decision-focused UX for three personas, and includes governance/feedback loops.

Let me know which components you'd like me to elaborate on or if you need specific implementation code for any service!
