create table user_groups (
   user_group_id         int primary key,
   user_group_name       varchar(100),
   user_group_valid_from date,
   user_group_valid_to   date,
   created_by            varchar(50),
   data_inserted         timestamp,
   updated_by            varchar(50),
   data_updated          timestamp
);

comment on table user_groups is
   'MAIN TABLE HOLDING USER GROUPS';

create index idx_user_groups_user_group_valid_to on
   user_groups (
      user_group_valid_to
   );