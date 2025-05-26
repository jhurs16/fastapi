truncate table user_objects;

insert into user_objects (
   user_object_parent_id,
   user_object_name,
   user_object_url,
   user_object_valid_from
) values ( 0,
           'ESG_DATA',
           'API_SCOPE',
           now() );