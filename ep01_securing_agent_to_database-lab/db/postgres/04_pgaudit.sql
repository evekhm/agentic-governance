-- Episode 01 Lab: pgaudit + sqlcommenter traceparent verification
-- Cloud SQL flag: cloudsql.enable_pgaudit = on, pgaudit.log = 'read,write,function'

CREATE EXTENSION IF NOT EXISTS pgaudit;

-- Verification query for T8 (run as auditor role in Phase 2/3):
-- SELECT name, setting FROM pg_settings WHERE name LIKE 'pgaudit%';
