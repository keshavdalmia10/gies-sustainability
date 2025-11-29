-- Gies Sustainability Impact Dashboard - Database Schema
-- PostgreSQL 15+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search

-- ============================================================================
-- CORE ENTITIES
-- ============================================================================

-- Faculty table
CREATE TABLE faculty (
    person_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    department VARCHAR(255),
    active BOOLEAN DEFAULT TRUE,
    profile_url TEXT,
    photo_url TEXT,
    research_interests TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_faculty_department ON faculty(department);
CREATE INDEX idx_faculty_active ON faculty(active);
CREATE INDEX idx_faculty_name_trgm ON faculty USING gin(name gin_trgm_ops);

-- Publications table
CREATE TABLE publications (
    article_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_uuid UUID REFERENCES faculty(person_uuid) ON DELETE CASCADE,
    title TEXT NOT NULL,
    abstract TEXT,
    publication_year INTEGER,
    doi VARCHAR(255),
    journal_title VARCHAR(255),
    journal_issn VARCHAR(50),
    keywords TEXT[],
    is_sustain BOOLEAN DEFAULT FALSE,
    sdg_top1 INTEGER CHECK (sdg_top1 BETWEEN 1 AND 17),
    sdg_top2 INTEGER CHECK (sdg_top2 BETWEEN 1 AND 17),
    sdg_top3 INTEGER CHECK (sdg_top3 BETWEEN 1 AND 17),
    sdg_confidence FLOAT CHECK (sdg_confidence BETWEEN 0 AND 1),
    citation_count INTEGER DEFAULT 0,
    source VARCHAR(100), -- 'Illinois Experts', 'PubMed', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_publications_person ON publications(person_uuid);
CREATE INDEX idx_publications_year ON publications(publication_year);
CREATE INDEX idx_publications_sdg1 ON publications(sdg_top1);
CREATE INDEX idx_publications_sustain ON publications(is_sustain);
CREATE INDEX idx_publications_doi ON publications(doi);

-- ============================================================================
-- IMPACT ENTITIES
-- ============================================================================

-- Impact entities (base table)
CREATE TABLE impacts (
    impact_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    impact_type VARCHAR(50) NOT NULL, -- 'grant', 'patent', 'policy', 'program'
    title TEXT NOT NULL,
    description TEXT,
    sdg_primary INTEGER CHECK (sdg_primary BETWEEN 1 AND 17),
    sdg_secondary INTEGER[] DEFAULT '{}',
    geography VARCHAR(255), -- 'Illinois', 'USA', 'Global'
    beneficiaries_count INTEGER,
    funding_amount DECIMAL(15,2),
    status VARCHAR(50), -- 'active', 'completed', 'pending'
    start_date DATE,
    end_date DATE,
    outcomes JSONB, -- Flexible structure for outcomes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_impacts_type ON impacts(impact_type);
CREATE INDEX idx_impacts_sdg_primary ON impacts(sdg_primary);
CREATE INDEX idx_impacts_status ON impacts(status);
CREATE INDEX idx_impacts_geography ON impacts(geography);

-- Grants (specialization of impacts)
CREATE TABLE grants (
    grant_id UUID PRIMARY KEY REFERENCES impacts(impact_id) ON DELETE CASCADE,
    external_id VARCHAR(255), -- NIH/NSF grant number
    funder VARCHAR(255) NOT NULL, -- 'NIH', 'NSF', 'DOE'
    funder_division VARCHAR(255),
    program VARCHAR(255),
    pi_uuid UUID REFERENCES faculty(person_uuid),
    co_investigators UUID[],
    keywords TEXT[],
    abstract TEXT,
    award_notice_date DATE
);

CREATE INDEX idx_grants_funder ON grants(funder);
CREATE INDEX idx_grants_pi ON grants(pi_uuid);
CREATE INDEX idx_grants_external_id ON grants(external_id);

-- Patents (specialization of impacts)
CREATE TABLE patents (
    patent_id UUID PRIMARY KEY REFERENCES impacts(impact_id) ON DELETE CASCADE,
    patent_number VARCHAR(50) UNIQUE NOT NULL,
    inventors UUID[], -- references to faculty
    assignee VARCHAR(255), -- University of Illinois
    classification_codes VARCHAR(50)[],
    citations_count INTEGER DEFAULT 0,
    grant_date DATE,
    filing_date DATE,
    patent_office VARCHAR(50) DEFAULT 'USPTO'
);

CREATE INDEX idx_patents_number ON patents(patent_number);
CREATE INDEX idx_patents_assignee ON patents(assignee);

-- Policy documents
CREATE TABLE policies (
    policy_id UUID PRIMARY KEY REFERENCES impacts(impact_id) ON DELETE CASCADE,
    agency VARCHAR(255) NOT NULL, -- 'IL EPA', 'USDA', etc.
    document_type VARCHAR(100), -- 'regulation', 'report', 'guideline'
    document_url TEXT,
    mention_type VARCHAR(50), -- 'research_cited', 'collaboration', 'expert_testimony'
    mentioned_faculty UUID[],
    publication_date DATE,
    effective_date DATE
);

CREATE INDEX idx_policies_agency ON policies(agency);

-- ============================================================================
-- LINKAGES
-- ============================================================================

-- Publication to Impact links
CREATE TABLE publication_impact_links (
    link_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    publication_uuid UUID REFERENCES publications(article_uuid) ON DELETE CASCADE,
    impact_id UUID REFERENCES impacts(impact_id) ON DELETE CASCADE,
    confidence_score FLOAT CHECK (confidence_score BETWEEN 0 AND 1),
    method VARCHAR(100), -- 'embedding_similarity', 'keyword_match', 'manual_validation'
    validated_by VARCHAR(255),
    is_validated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(publication_uuid, impact_id)
);

CREATE INDEX idx_pub_impact_pub ON publication_impact_links(publication_uuid);
CREATE INDEX idx_pub_impact_impact ON publication_impact_links(impact_id);
CREATE INDEX idx_pub_impact_confidence ON publication_impact_links(confidence_score);

-- Faculty to Impact links
CREATE TABLE faculty_impact_links (
    link_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_uuid UUID REFERENCES faculty(person_uuid) ON DELETE CASCADE,
    impact_id UUID REFERENCES impacts(impact_id) ON DELETE CASCADE,
    role VARCHAR(100), -- 'PI', 'co-PI', 'inventor', 'expert', 'collaborator'
    contribution_percentage INTEGER CHECK (contribution_percentage BETWEEN 0 AND 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(person_uuid, impact_id, role)
);

CREATE INDEX idx_faculty_impact_faculty ON faculty_impact_links(person_uuid);
CREATE INDEX idx_faculty_impact_impact ON faculty_impact_links(impact_id);

-- ============================================================================
-- EVALUATION & GROUND TRUTH
-- ============================================================================

-- Ground truth for model evaluation
CREATE TABLE ground_truth_set (
    gt_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    publication_uuid UUID REFERENCES publications(article_uuid),
    impact_id UUID REFERENCES impacts(impact_id),
    is_true_link BOOLEAN NOT NULL,
    sdg INTEGER CHECK (sdg BETWEEN 1 AND 17),
    validated_by VARCHAR(255) NOT NULL,
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validation_method VARCHAR(100), -- 'expert_review', 'cross_validation'
    notes TEXT,
    UNIQUE(publication_uuid, impact_id)
);

CREATE INDEX idx_gt_sdg ON ground_truth_set(sdg);
CREATE INDEX idx_gt_validated ON ground_truth_set(is_true_link);

-- Model evaluation results
CREATE TABLE model_evaluations (
    eval_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_version VARCHAR(100) NOT NULL,
    model_type VARCHAR(50), -- 'sdg_classifier', 'impact_matcher'
    sdg INTEGER CHECK (sdg BETWEEN 1 AND 17),
    precision_at_k FLOAT,
    recall_at_k FLOAT,
    f1_at_k FLOAT,
    k INTEGER,
    evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    test_set_size INTEGER,
    parameters JSONB, -- Model hyperparameters
    notes TEXT
);

CREATE INDEX idx_eval_model_version ON model_evaluations(model_version);
CREATE INDEX idx_eval_sdg ON model_evaluations(sdg);

-- ============================================================================
-- GOVERNANCE & FEEDBACK
-- ============================================================================

-- Faculty feedback
CREATE TABLE faculty_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_uuid UUID REFERENCES faculty(person_uuid),
    feedback_type VARCHAR(50) NOT NULL, -- 'correction', 'opt_out', 'add_impact'
    entity_type VARCHAR(50), -- 'publication', 'impact', 'link', 'sdg_classification'
    entity_id UUID,
    original_value TEXT,
    suggested_value TEXT,
    comments TEXT,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'resolved'
    reviewed_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE INDEX idx_feedback_person ON faculty_feedback(person_uuid);
CREATE INDEX idx_feedback_status ON faculty_feedback(status);
CREATE INDEX idx_feedback_type ON faculty_feedback(feedback_type);

-- Data retention policies
CREATE TABLE data_retention_policies (
    policy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL, -- 'logs', 'feedback', 'evaluations'
    retention_days INTEGER NOT NULL,
    description TEXT,
    last_purge_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255),
    action VARCHAR(100) NOT NULL, -- 'create', 'update', 'delete', 'view'
    entity_type VARCHAR(50),
    entity_id UUID,
    changes JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_created ON audit_logs(created_at);
CREATE INDEX idx_logs_entity ON audit_logs(entity_type, entity_id);

-- ============================================================================
-- IMPACT CARDS
-- ============================================================================

-- Impact cards
CREATE TABLE impact_cards (
    card_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_uuid UUID REFERENCES faculty(person_uuid) ON DELETE CASCADE,
    sdg INTEGER NOT NULL CHECK (sdg BETWEEN 1 AND 17),
    title VARCHAR(500) NOT NULL,
    summary TEXT NOT NULL,
    narrative TEXT, -- LLM-generated story
    publications UUID[],
    impacts UUID[],
    key_outcomes TEXT[], -- ['200 jobs created', '50MW solar capacity']
    geography VARCHAR(255),
    total_funding DECIMAL(15,2),
    communities_reached INTEGER,
    start_year INTEGER,
    end_year INTEGER,
    funding_gap DECIMAL(15,2),
    next_milestones TEXT[],
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'validated', 'published'
    validated_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(person_uuid, sdg)
);

CREATE INDEX idx_cards_person ON impact_cards(person_uuid);
CREATE INDEX idx_cards_sdg ON impact_cards(sdg);
CREATE INDEX idx_cards_status ON impact_cards(status);

-- ============================================================================
-- SDG REFERENCE DATA
-- ============================================================================

-- SDG reference table
CREATE TABLE sdg_goals (
    sdg_number INTEGER PRIMARY KEY CHECK (sdg_number BETWEEN 1 AND 17),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    color_hex VARCHAR(7), -- e.g., '#E5243B' for SDG1
    icon_url TEXT,
    keywords TEXT[]
);

-- Populate SDG goals
INSERT INTO sdg_goals (sdg_number, title, description, color_hex) VALUES
(1, 'No Poverty', 'End poverty in all its forms everywhere', '#E5243B'),
(2, 'Zero Hunger', 'End hunger, achieve food security and improved nutrition', '#DDA63A'),
(3, 'Good Health and Well-being', 'Ensure healthy lives and promote well-being', '#4C9F38'),
(4, 'Quality Education', 'Ensure inclusive and equitable quality education', '#C5192D'),
(5, 'Gender Equality', 'Achieve gender equality and empower all women and girls', '#FF3A21'),
(6, 'Clean Water and Sanitation', 'Ensure availability and sustainable management of water', '#26BDE2'),
(7, 'Affordable and Clean Energy', 'Ensure access to affordable, reliable, sustainable energy', '#FCC30B'),
(8, 'Decent Work and Economic Growth', 'Promote sustained, inclusive and sustainable economic growth', '#A21942'),
(9, 'Industry, Innovation and Infrastructure', 'Build resilient infrastructure, promote sustainable industrialization', '#FD6925'),
(10, 'Reduced Inequality', 'Reduce inequality within and among countries', '#DD1367'),
(11, 'Sustainable Cities and Communities', 'Make cities and human settlements inclusive, safe, resilient', '#FD9D24'),
(12, 'Responsible Consumption and Production', 'Ensure sustainable consumption and production patterns', '#BF8B2E'),
(13, 'Climate Action', 'Take urgent action to combat climate change', '#3F7E44'),
(14, 'Life Below Water', 'Conserve and sustainably use the oceans, seas and marine resources', '#0A97D9'),
(15, 'Life on Land', 'Protect, restore and promote sustainable use of terrestrial ecosystems', '#56C02B'),
(16, 'Peace, Justice and Strong Institutions', 'Promote peaceful and inclusive societies', '#00689D'),
(17, 'Partnerships for the Goals', 'Strengthen the means of implementation', '#19486A');

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Faculty with publication counts by SDG
CREATE VIEW faculty_sdg_summary AS
SELECT 
    f.person_uuid,
    f.name,
    f.department,
    p.sdg_top1 as sdg,
    COUNT(*) as publication_count,
    AVG(p.sdg_confidence) as avg_confidence,
    MAX(p.publication_year) as latest_publication_year
FROM faculty f
LEFT JOIN publications p ON f.person_uuid = p.person_uuid
WHERE p.is_sustain = TRUE AND p.sdg_top1 IS NOT NULL
GROUP BY f.person_uuid, f.name, f.department, p.sdg_top1;

-- View: Impact card summary
CREATE VIEW impact_card_summary AS
SELECT 
    ic.*,
    f.name as faculty_name,
    f.department,
    sg.title as sdg_title,
    sg.color_hex as sdg_color,
    array_length(ic.publications, 1) as publication_count,
    array_length(ic.impacts, 1) as impact_count
FROM impact_cards ic
JOIN faculty f ON ic.person_uuid = f.person_uuid
JOIN sdg_goals sg ON ic.sdg = sg.sdg_number
WHERE ic.status = 'published';

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_faculty_updated_at BEFORE UPDATE ON faculty
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_publications_updated_at BEFORE UPDATE ON publications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_impacts_updated_at BEFORE UPDATE ON impacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_impact_cards_updated_at BEFORE UPDATE ON impact_cards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA RETENTION POLICIES
-- ============================================================================

INSERT INTO data_retention_policies (entity_type, retention_days, description) VALUES
('audit_logs', 730, 'Audit logs retained for 2 years'),
('feedback', -1, 'Feedback retained indefinitely'),
('evaluations', -1, 'Model evaluations retained indefinitely'),
('temp_embeddings', 90, 'Temporary embeddings purged after 90 days');

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE faculty IS 'Core faculty information';
COMMENT ON TABLE publications IS 'Faculty publications with SDG classifications';
COMMENT ON TABLE impacts IS 'Real-world impacts (grants, patents, policies)';
COMMENT ON TABLE publication_impact_links IS 'Links between publications and impacts with confidence scores';
COMMENT ON TABLE ground_truth_set IS 'Manually validated links for model evaluation';
COMMENT ON TABLE model_evaluations IS 'Precision@k and other model performance metrics';
COMMENT ON TABLE impact_cards IS 'Rich impact narratives for decision-makers';
