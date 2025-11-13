-- =============================================================================
-- Enable pgvector extension for vector similarity search
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- Verify extension is enabled
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        RAISE EXCEPTION 'Failed to enable vector extension';
    END IF;
    RAISE NOTICE 'Vector extension successfully enabled';
END $$;
