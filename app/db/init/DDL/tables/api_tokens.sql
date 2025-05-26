create table api_tokens (
   api_token_id         int primary key,
   api_token            varchar(2000),
   user_id              int default null,
   api_client_id        int default null,
   api_user_id          int default null,
   api_token_type       varchar(255),
   api_token_valid_from date,
   api_token_valid_to   date,
   created_by           varchar(50),
   data_inserted        timestamp,
   data_updated         timestamp
);

comment on table api_tokens is
   'table to hold tokens which have been generated in different context';

create index idx_api_tokens_user_id on
   api_tokens (
      user_id
   );
create index idx_api_tokens_api_client_id on
   api_tokens (
      api_client_id
   );
create index idx_api_tokens_api_user_id on
   api_tokens (
      api_user_id
   );
create index idx_api_tokens_api_token_valid_to on
   api_tokens (
      api_token_valid_to
   );