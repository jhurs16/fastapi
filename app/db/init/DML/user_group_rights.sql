truncate table user_group_rights;

insert into user_group_rights (
   user_group_right_id,
   user_group_id,
   user_object_id,
   user_group_right_read,
   user_group_right_write,
   user_group_right_execute,
   user_group_right_delete,
   user_group_right_valid_from
)
   select 1,
          user_group_id,
          user_object_id,
          'N',
          'N',
          'N',
          'N',
          now()
     from user_groups
     left join user_objects
   on 1 = 1;

update user_group_rights
   set user_group_right_write = 'N',
       user_group_right_read = 'Y',
       user_group_right_execute = 'N'
 where user_group_id in (
   select user_group_id
     from user_groups
    where user_group_name = 'STANDARD USER GROUP'
)
   and user_object_id in (
   select user_object_id
     from user_objects
    where user_object_name in ( 'ESG_DATA' )
);