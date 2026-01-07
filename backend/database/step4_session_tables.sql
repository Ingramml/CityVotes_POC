-- =============================================================================
-- STEP 4: Create Session Tables (for web app)
-- =============================================================================

-- Sessions table
CREATE TABLE sessions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at          TIMESTAMP DEFAULT NOW(),
    expires_at          TIMESTAMP DEFAULT NOW() + INTERVAL '2 hours',
    ip_address          INET,
    user_agent          TEXT
);

COMMENT ON TABLE sessions IS 'Web application user sessions';
COMMENT ON COLUMN sessions.expires_at IS 'Session expires 2 hours after creation';

CREATE INDEX idx_sessions_expires ON sessions(expires_at);

-- Session data table
CREATE TABLE session_data (
    id                  SERIAL PRIMARY KEY,
    session_id          UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    city_id             INTEGER NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    original_filename   VARCHAR(255),
    upload_timestamp    TIMESTAMP DEFAULT NOW(),
    raw_data            JSONB NOT NULL,
    processed_data      JSONB NOT NULL,
    vote_count          INTEGER DEFAULT 0,
    CONSTRAINT uq_session_data_session_city UNIQUE (session_id, city_id)
);

COMMENT ON TABLE session_data IS 'Uploaded voting data for each session';
COMMENT ON COLUMN session_data.raw_data IS 'Original uploaded JSON';
COMMENT ON COLUMN session_data.processed_data IS 'Pre-calculated summaries';

CREATE INDEX idx_session_data_session ON session_data(session_id);
CREATE INDEX idx_session_data_city ON session_data(city_id);
CREATE INDEX idx_session_data_raw ON session_data USING gin(raw_data);
CREATE INDEX idx_session_data_processed ON session_data USING gin(processed_data);

-- Verify tables created
SELECT 'Step 4 Complete: Session tables created' as status;
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;
