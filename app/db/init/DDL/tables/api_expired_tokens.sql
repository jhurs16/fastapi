create table api_expired_tokens (
   api_expired_token_id         int primary key,
   api_expired_token            varchar(4000),
   api_expired_token_valid_from date,
   api_expired_token_valid_to   date,
   created_by                   varchar(50),
   data_inserted                timestamp,
   updated_by                   varchar(50),
   data_updated                 timestamp
);

comment on table api_expired_tokens is
   'TABLE TO HOLD EXPIRED TOKENS TO BE CHECKED';

create index idx_aet_api_expired_token on
   api_expired_tokens (
      api_expired_token
   );
create index idx_aet_api_expired_token_valid_to on
   api_expired_tokens (
      api_expired_token_valid_to
   );