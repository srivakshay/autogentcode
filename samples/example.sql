CREATE OR REPLACE PROCEDURE process_orders(p_min_total NUMERIC)
LANGUAGE plpgsql
AS $$
BEGIN
  -- Example: mark orders above threshold as PRIORITY
  UPDATE orders
     SET priority = TRUE
   WHERE total_amount >= p_min_total
     AND status = 'NEW';
END;
$$;
