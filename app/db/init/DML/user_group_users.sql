delete from user_group_users;

insert into user_group_users (
   user_group_id,
   user_id,
   user_group_users_valid_from
)
   select (
      select user_group_id
        from user_groups
       where user_group_name = 'STANDARD USER GROUP'
   ),
          u.user_id,
          now()
     from "USER" u;