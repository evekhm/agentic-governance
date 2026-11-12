-- Episode 01 Lab: Transaction-Local SET LOCAL + FORCE ROW LEVEL SECURITY + Idempotent Stored Proc

ALTER TABLE sales.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales.orders FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS agent_user_isolation ON sales.orders;
CREATE POLICY agent_user_isolation ON sales.orders AS RESTRICTIVE
    FOR SELECT TO toolbox_read_sa
    USING (
        owner_email = NULLIF(current_setting('app.current_user_email', true), '')
        OR user_id = NULLIF(current_setting('app.current_user_id', true), '')
    );

CREATE OR REPLACE FUNCTION sales.refund_order(
    p_owner_email TEXT,
    p_order_id TEXT,
    p_amount_usd NUMERIC,
    p_reason_code TEXT,
    p_idempotency_key TEXT
)
RETURNS TABLE (
    status TEXT,
    order_id TEXT,
    amount_usd NUMERIC,
    idempotency_key TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = sales, pg_temp
AS $$
DECLARE
    v_order sales.orders%ROWTYPE;
    v_existing sales.refund_ledger%ROWTYPE;
BEGIN
    IF p_owner_email IS NULL OR p_owner_email = '' THEN
        RAISE EXCEPTION 'Missing authenticated caller email';
    END IF;
    IF p_amount_usd <= 0 OR p_amount_usd > 500 THEN
        RAISE EXCEPTION 'Refund amount % out of bounds (0, 500]', p_amount_usd;
    END IF;
    IF p_reason_code NOT IN ('DAMAGED', 'LATE_DELIVERY', 'WRONG_ITEM') THEN
        RAISE EXCEPTION 'Invalid reason code: %', p_reason_code;
    END IF;

    SELECT * INTO v_existing
    FROM sales.refund_ledger
    WHERE refund_ledger.idempotency_key = p_idempotency_key;

    IF FOUND THEN
        RETURN QUERY SELECT v_existing.status, v_existing.order_id, v_existing.amount_usd, v_existing.idempotency_key;
        RETURN;
    END IF;

    SELECT * INTO v_order
    FROM sales.orders
    WHERE orders.order_id = p_order_id
      AND orders.owner_email = p_owner_email
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Order % not found for caller %', p_order_id, p_owner_email;
    END IF;

    IF p_amount_usd > v_order.total THEN
        RAISE EXCEPTION 'Refund amount % exceeds order total %', p_amount_usd, v_order.total;
    END IF;

    INSERT INTO sales.refund_ledger (idempotency_key, order_id, user_id, amount_usd, reason_code, status)
    VALUES (p_idempotency_key, v_order.order_id, v_order.user_id, p_amount_usd, p_reason_code, 'REFUNDED');

    UPDATE sales.orders
    SET status = 'REFUND_REQUESTED', updated_at = NOW()
    WHERE orders.order_id = v_order.order_id;

    RETURN QUERY SELECT 'REFUNDED'::TEXT, v_order.order_id, p_amount_usd, p_idempotency_key;
END;
$$;

REVOKE ALL ON FUNCTION sales.refund_order(TEXT, TEXT, NUMERIC, TEXT, TEXT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION sales.refund_order(TEXT, TEXT, NUMERIC, TEXT, TEXT) TO toolbox_write_sa;
