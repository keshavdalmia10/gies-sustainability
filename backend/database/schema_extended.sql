-- Additional data types for comprehensive sustainability impact tracking
-- Run after main schema.sql

-- Course Curricula Table
CREATE TABLE IF NOT EXISTS course_curricula (
    course_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_code VARCHAR(20) NOT NULL,
    course_name VARCHAR(255) NOT NULL,
    instructor_uuid UUID REFERENCES faculty(person_uuid) ON DELETE SET NULL,
    department VARCHAR(100),
    semester VARCHAR(20),
    year INTEGER,
    sdg_primary INTEGER REFERENCES sdg_goals(sdg_number),
    sdg_secondary INTEGER[],
    description TEXT,
    syllabus_url VARCHAR(500),
    sustainability_topics TEXT[],
    learning_outcomes TEXT[],
    enrollment_count INTEGER,
    student_projects_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_course_instructor ON course_curricula(instructor_uuid);
CREATE INDEX idx_course_sdg ON course_curricula(sdg_primary);
CREATE INDEX idx_course_year ON course_curricula(year);
CREATE INDEX idx_course_code ON course_curricula(course_code);

-- Student Projects Table
CREATE TABLE IF NOT EXISTS student_projects (
    project_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_title VARCHAR(500) NOT NULL,
    project_type VARCHAR(50), -- capstone, thesis, research, competition
    course_id UUID REFERENCES course_curricula(course_id) ON DELETE SET NULL,
    advisor_uuid UUID REFERENCES faculty(person_uuid) ON DELETE SET NULL,
    student_names TEXT[],
    sdg_primary INTEGER REFERENCES sdg_goals(sdg_number),
    sdg_secondary INTEGER[],
    description TEXT,
    abstract TEXT,
    outcomes TEXT,
    award_received VARCHAR(255),
    presentation_date DATE,
    project_year INTEGER,
    repository_url VARCHAR(500),
    publication_resulted BOOLEAN DEFAULT FALSE,
    community_partner VARCHAR(255),
    impact_metrics JSONB, -- {communities_reached: 100, etc}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_student_project_advisor ON student_projects(advisor_uuid);
CREATE INDEX idx_student_project_course ON student_projects(course_id);
CREATE INDEX idx_student_project_sdg ON student_projects(sdg_primary);
CREATE INDEX idx_student_project_year ON student_projects(project_year);

-- Corporate Partnerships Table
CREATE TABLE IF NOT EXISTS corporate_partnerships (
    partnership_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partnership_name VARCHAR(255) NOT NULL,
    corporate_partner VARCHAR(255) NOT NULL,
    faculty_lead_uuid UUID REFERENCES faculty(person_uuid) ON DELETE SET NULL,
    partnership_type VARCHAR(100), -- research, sponsorship, internship, consulting
    sdg_primary INTEGER REFERENCES sdg_goals(sdg_number),
    sdg_secondary INTEGER[],
    description TEXT,
    start_date DATE,
    end_date DATE,
    funding_amount DECIMAL(15, 2),
    deliverables TEXT[],
    outcomes TEXT,
    student_participants_count INTEGER,
    publications_count INTEGER DEFAULT 0,
    patents_count INTEGER DEFAULT 0,
    industry_sector VARCHAR(100),
    geography VARCHAR(100),
    status VARCHAR(50), -- active, completed, pending
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_partnership_faculty ON corporate_partnerships(faculty_lead_uuid);
CREATE INDEX idx_partnership_sdg ON corporate_partnerships(sdg_primary);
CREATE INDEX idx_partnership_status ON corporate_partnerships(status);
CREATE INDEX idx_partnership_sector ON corporate_partnerships(industry_sector);

-- Enhanced Policies Table (extending existing schema)
-- This adds metadata to the existing policies table

ALTER TABLE IF EXISTS policies 
ADD COLUMN IF NOT EXISTS policy_type VARCHAR(100), -- federal, state, local, international
ADD COLUMN IF NOT EXISTS jurisdiction VARCHAR(100),
ADD COLUMN IF NOT EXISTS policy_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS faculty_contributor_uuids UUID[],
ADD COLUMN IF NOT EXISTS implementation_status VARCHAR(50), -- proposed, enacted, implemented
ADD COLUMN IF NOT EXISTS policy_impact_description TEXT,
ADD COLUMN IF NOT EXISTS citations_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS media_coverage TEXT[];

CREATE INDEX IF NOT EXISTS idx_policy_type ON policies(policy_type);
CREATE INDEX IF NOT EXISTS idx_policy_jurisdiction ON policies(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_policy_status ON policies(implementation_status);

-- Link tables for relationships

-- Course-Publication Links (when course leads to publication)
CREATE TABLE IF NOT EXISTS course_publication_links (
    link_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES course_curricula(course_id) ON DELETE CASCADE,
    publication_uuid UUID REFERENCES publications(article_uuid) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(course_id, publication_uuid)
);

-- Partnership-Publication Links
CREATE TABLE IF NOT EXISTS partnership_publication_links (
    link_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partnership_id UUID REFERENCES corporate_partnerships(partnership_id) ON DELETE CASCADE,
    publication_uuid UUID REFERENCES publications(article_uuid) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(partnership_id, publication_uuid)
);

-- Student Project-Impact Links
CREATE TABLE IF NOT EXISTS project_impact_links (
    link_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES student_projects(project_id) ON DELETE CASCADE,
    impact_id UUID REFERENCES impacts(impact_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, impact_id)
);

-- Views for common queries

-- Faculty teaching sustainability
CREATE OR REPLACE VIEW faculty_sustainability_teaching AS
SELECT 
    f.person_uuid,
    f.name,
    f.department,
    COUNT(DISTINCT cc.course_id) as sustainability_courses_count,
    ARRAY_AGG(DISTINCT cc.sdg_primary) FILTER (WHERE cc.sdg_primary IS NOT NULL) as sdgs_taught,
    SUM(cc.enrollment_count) as total_students_reached,
    SUM(cc.student_projects_count) as total_student_projects
FROM faculty f
JOIN course_curricula cc ON f.person_uuid = cc.instructor_uuid
WHERE cc.sdg_primary IS NOT NULL
GROUP BY f.person_uuid, f.name, f.department;

-- Partnership portfolio by SDG
CREATE OR REPLACE VIEW partnerships_by_sdg AS
SELECT 
    sdg.sdg_number,
    sdg.title as sdg_title,
    COUNT(cp.partnership_id) as partnership_count,
    SUM(cp.funding_amount) as total_funding,
    ARRAY_AGG(cp.corporate_partner) as partners
FROM sdg_goals sdg
LEFT JOIN corporate_partnerships cp ON sdg.sdg_number = cp.sdg_primary
GROUP BY sdg.sdg_number, sdg.title
ORDER BY partnership_count DESC;

-- Student impact summary
CREATE OR REPLACE VIEW student_impact_summary AS
SELECT 
    sp.project_year,
    sp.sdg_primary,
    COUNT(sp.project_id) as project_count,
    COUNT(DISTINCT sp.advisor_uuid) as faculty_advisors,
    SUM(CASE WHEN sp.publication_resulted THEN 1 ELSE 0 END) as publications_resulted,
    COUNT(DISTINCT sp.community_partner) FILTER (WHERE sp.community_partner IS NOT NULL) as community_partners
FROM student_projects sp
GROUP BY sp.project_year, sp.sdg_primary;

-- Triggers for updated_at

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_course_timestamp
    BEFORE UPDATE ON course_curricula
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_student_project_timestamp
    BEFORE UPDATE ON student_projects
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_partnership_timestamp
    BEFORE UPDATE ON corporate_partnerships
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();
