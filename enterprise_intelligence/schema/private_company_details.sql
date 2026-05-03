-- SQL schema for private company detailscreate table private_company_details (
    id bigint generated always as identity primary key,
    file_name text not null,
    title text,
    page_number integer,
    content text not null,
    category text default 'private',
    source text default 'uploaded_pdf',
    created_at timestamp default now()
);

create index idx_private_company_content
on private_company_details using gin(to_tsvector('english', content));