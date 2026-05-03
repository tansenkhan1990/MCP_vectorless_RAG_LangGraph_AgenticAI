-- Vectorless RAG Database Schema for Supabase
-- This schema creates tables, indexes, and triggers for document storage and full-text search.

-- Enable required extensions
create extension if not exists pgcrypto;

create table private_company_details (
    id bigint generated always as identity primary key,
    file_name text,
    title text,
    page_number integer,
    chunk_text text not null,
    category text default 'private',
    source text default 'uploaded_pdf',
    created_at timestamp default now(),
    tsv tsvector
);

create index idx_private_company_chunk_text
on private_company_details using gin(tsv);

create or replace function update_tsv()
returns trigger as $$
begin
    new.tsv := to_tsvector('english', coalesce(new.chunk_text, ''));
    return new;
end
$$ language plpgsql;

drop trigger if exists trg_private_company_details_tsv on private_company_details;

drop function if exists search_private_company_details(text, int);

create trigger trg_private_company_details_tsv
before insert or update
on private_company_details
for each row execute function update_tsv();

create function search_private_company_details(
    search_query text,
    match_count int
)
returns table(
    file_name text,
    title text,
    page_number int,
    chunk_text text,
    category text,
    source text,
    created_at timestamp
)
language sql
as $$
select file_name, title, page_number, chunk_text, category, source, created_at
from private_company_details
where tsv @@ plainto_tsquery(search_query)
order by ts_rank(tsv, plainto_tsquery(search_query)) desc
limit match_count;
$$;