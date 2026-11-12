-- Episode 01 Lab: Column Grants + PostgreSQL 15+ Security-Invoker View
-- Replace toolbox-read-sa@<project>.iam and toolbox-write-sa@<project>.iam when provisioning.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'toolbox_read_sa') THEN
        CREATE ROLE toolbox_read_sa NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'toolbox_write_sa') THEN
        CREATE ROLE toolbox_write_sa NOLOGIN;
    END IF;
END $$;

REVOKE ALL ON SCHEMA sales FROM PUBLIC;
GRANT USAGE ON SCHEMA sales TO toolbox_read_sa, toolbox_write_sa;

REVOKE ALL ON TABLE sales.customers FROM PUBLIC, toolbox_read_sa, toolbox_write_sa;
REVOKE ALL ON TABLE sales.orders FROM PUBLIC, toolbox_read_sa, toolbox_write_sa;
REVOKE ALL ON TABLE sales.refund_ledger FROM PUBLIC, toolbox_read_sa, toolbox_write_sa;

GRANT SELECT (order_id, user_id, owner_email, status, total, contact_phone, delivery_notes, updated_at)
    ON TABLE sales.orders TO toolbox_read_sa;

CREATE OR REPLACE VIEW sales.agent_orders_v WITH (security_invoker = true) AS
SELECT
    order_id,
    user_id,
    owner_email,
    status,
    total,
    '***-***-' || right(contact_phone, 4) AS phone_masked,
    delivery_notes,
    updated_at
FROM sales.orders;

GRANT SELECT ON sales.agent_orders_v TO toolbox_read_sa;
