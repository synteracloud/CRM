set search_path to transaction_db, public;

drop function if exists transaction_db.apply_payment_status_transition(uuid, uuid, text, timestamptz, text, uuid);
drop function if exists transaction_db.is_valid_payment_status_transition(text, text);

drop table if exists revenue_ledger;
drop table if exists payment_status_history;
drop trigger if exists trg_payment_updated_at on payment;
drop table if exists payment;
