set search_path to transaction_db, public;

drop table if exists idempotency_key;
drop table if exists outbox_event;
