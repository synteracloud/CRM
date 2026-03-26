set search_path to transaction_db, public;

drop table if exists payment_event;
drop table if exists invoice_summary;
drop table if exists subscription;
drop table if exists tenant_ref;

drop function if exists transaction_db.set_updated_at();
