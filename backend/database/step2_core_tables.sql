-- =============================================================================
-- STEP 2: Create Core Tables (cities, council_members, council_member_terms)
-- =============================================================================

-- Cities table
CREATE TABLE cities (
    id                  SERIAL PRIMARY KEY,
    city_key            VARCHAR(50) UNIQUE NOT NULL,
    name                VARCHAR(100) NOT NULL,
    display_name        VARCHAR(150) NOT NULL,
    state               VARCHAR(2) DEFAULT 'CA',
    total_seats         INTEGER NOT NULL DEFAULT 7,
    primary_color       VARCHAR(7) DEFAULT '#1f4e79',
    secondary_color     VARCHAR(7) DEFAULT '#f4b942',
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE cities IS 'City configuration and branding settings';
COMMENT ON COLUMN cities.city_key IS 'URL-safe identifier (e.g., santa_ana)';
COMMENT ON COLUMN cities.total_seats IS 'Number of council seats';

-- Council members table
CREATE TABLE council_members (
    id                  SERIAL PRIMARY KEY,
    city_id             INTEGER NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    member_key          VARCHAR(50) NOT NULL,
    full_name           VARCHAR(150) NOT NULL,
    short_name          VARCHAR(50) NOT NULL,
    title               VARCHAR(50),
    district            INTEGER,
    term_start          DATE,
    term_end            DATE,
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_council_members_city_key UNIQUE (city_id, member_key)
);

COMMENT ON TABLE council_members IS 'Council members for each city';
COMMENT ON COLUMN council_members.member_key IS 'URL-safe identifier (e.g., amezcua)';
COMMENT ON COLUMN council_members.short_name IS 'Name as appears in vote records';

CREATE INDEX idx_council_members_city ON council_members(city_id);
CREATE INDEX idx_council_members_active ON council_members(city_id, is_active);

-- Council member terms table (tracks position changes over time)
CREATE TABLE council_member_terms (
    id                  SERIAL PRIMARY KEY,
    member_id           INTEGER NOT NULL REFERENCES council_members(id) ON DELETE CASCADE,
    position            VARCHAR(50) NOT NULL DEFAULT 'Council Member',
    district            INTEGER,
    term_start          DATE NOT NULL,
    term_end            DATE,
    election_date       DATE,
    appointment_type    VARCHAR(50) DEFAULT 'elected',
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW(),
    CONSTRAINT chk_term_dates CHECK (term_end IS NULL OR term_end > term_start),
    CONSTRAINT chk_appointment_type CHECK (appointment_type IN ('elected', 'appointed', 'interim'))
);

COMMENT ON TABLE council_member_terms IS 'Tracks council member positions over time';
COMMENT ON COLUMN council_member_terms.position IS 'Mayor, Vice Mayor, Council Member, etc.';
COMMENT ON COLUMN council_member_terms.term_end IS 'NULL indicates currently serving';

CREATE INDEX idx_council_member_terms_member ON council_member_terms(member_id);
CREATE INDEX idx_council_member_terms_dates ON council_member_terms(term_start, term_end);
CREATE INDEX idx_council_member_terms_active ON council_member_terms(member_id) WHERE term_end IS NULL;

-- Verify tables created
SELECT 'Step 2 Complete: Core tables created' as status;
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;
