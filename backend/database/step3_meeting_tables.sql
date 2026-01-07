-- =============================================================================
-- STEP 3: Create Meeting Tables (meetings, agenda_items, votes, member_votes)
-- =============================================================================

-- Meetings table
CREATE TABLE meetings (
    id                  SERIAL PRIMARY KEY,
    city_id             INTEGER NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    meeting_date        DATE NOT NULL,
    meeting_type        VARCHAR(50) NOT NULL DEFAULT 'regular',
    meeting_year        INTEGER GENERATED ALWAYS AS (EXTRACT(YEAR FROM meeting_date)) STORED,
    meeting_month       INTEGER GENERATED ALWAYS AS (EXTRACT(MONTH FROM meeting_date)) STORED,
    start_time          TIME,
    end_time            TIME,
    location            VARCHAR(255),
    agenda_url          TEXT,
    minutes_url         TEXT,
    video_url           TEXT,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_meetings_city_date_type UNIQUE (city_id, meeting_date, meeting_type)
);

COMMENT ON TABLE meetings IS 'City council meetings';
COMMENT ON COLUMN meetings.meeting_type IS 'regular, special, emergency, closed';

CREATE INDEX idx_meetings_city ON meetings(city_id);
CREATE INDEX idx_meetings_date ON meetings(meeting_date DESC);
CREATE INDEX idx_meetings_year ON meetings(city_id, meeting_year);
CREATE INDEX idx_meetings_city_date ON meetings(city_id, meeting_date DESC);

-- Agenda items table
CREATE TABLE agenda_items (
    id                  SERIAL PRIMARY KEY,
    meeting_id          INTEGER NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    item_number         VARCHAR(20) NOT NULL,
    title               TEXT NOT NULL,
    description         TEXT,
    section             VARCHAR(50) NOT NULL DEFAULT 'GENERAL',
    department          VARCHAR(150),
    recommended_action  TEXT,
    fiscal_impact       TEXT,
    is_public_hearing   BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_agenda_items_meeting_number UNIQUE (meeting_id, item_number)
);

COMMENT ON TABLE agenda_items IS 'Individual agenda items for each meeting';
COMMENT ON COLUMN agenda_items.section IS 'CONSENT, BUSINESS, PUBLIC_HEARING, CLOSED';

CREATE INDEX idx_agenda_items_meeting ON agenda_items(meeting_id);
CREATE INDEX idx_agenda_items_section ON agenda_items(section);
CREATE INDEX idx_agenda_items_title_gin ON agenda_items USING gin(to_tsvector('english', title));

-- Votes table
CREATE TABLE votes (
    id                  SERIAL PRIMARY KEY,
    agenda_item_id      INTEGER NOT NULL REFERENCES agenda_items(id) ON DELETE CASCADE,
    example_id          VARCHAR(50) UNIQUE,
    outcome             VARCHAR(20) NOT NULL,
    ayes                INTEGER DEFAULT 0,
    noes                INTEGER DEFAULT 0,
    abstain             INTEGER DEFAULT 0,
    absent              INTEGER DEFAULT 0,
    recusal             INTEGER DEFAULT 0,
    motion_by           INTEGER REFERENCES council_members(id),
    seconded_by         INTEGER REFERENCES council_members(id),
    vote_number         INTEGER DEFAULT 1,
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE votes IS 'Vote records for agenda items';
COMMENT ON COLUMN votes.outcome IS 'PASS, FAIL, FLAG, CONTINUED, REMOVED, TIE';
COMMENT ON COLUMN votes.example_id IS 'Original ID from data extraction';

CREATE INDEX idx_votes_agenda_item ON votes(agenda_item_id);
CREATE INDEX idx_votes_outcome ON votes(outcome);
CREATE INDEX idx_votes_example_id ON votes(example_id);

-- Member votes table
CREATE TABLE member_votes (
    id                  SERIAL PRIMARY KEY,
    vote_id             INTEGER NOT NULL REFERENCES votes(id) ON DELETE CASCADE,
    member_id           INTEGER NOT NULL REFERENCES council_members(id) ON DELETE CASCADE,
    term_id             INTEGER REFERENCES council_member_terms(id) ON DELETE SET NULL,
    vote_choice         VARCHAR(20) NOT NULL,
    created_at          TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_member_votes_vote_member UNIQUE (vote_id, member_id),
    CONSTRAINT chk_vote_choice CHECK (vote_choice IN ('AYE', 'NAY', 'ABSTAIN', 'ABSENT', 'RECUSAL'))
);

COMMENT ON TABLE member_votes IS 'Individual council member vote choices';
COMMENT ON COLUMN member_votes.vote_choice IS 'AYE, NAY, ABSTAIN, ABSENT, RECUSAL';
COMMENT ON COLUMN member_votes.term_id IS 'Links to term when vote was cast';

CREATE INDEX idx_member_votes_vote ON member_votes(vote_id);
CREATE INDEX idx_member_votes_member ON member_votes(member_id);
CREATE INDEX idx_member_votes_term ON member_votes(term_id);
CREATE INDEX idx_member_votes_choice ON member_votes(vote_choice);
CREATE INDEX idx_member_votes_member_choice ON member_votes(member_id, vote_choice);

-- Verify tables created
SELECT 'Step 3 Complete: Meeting tables created' as status;
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;
