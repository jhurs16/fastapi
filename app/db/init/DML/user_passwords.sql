insert into user_passwords (
   user_id,
   user_password,
   user_password_valid_from
) values ( 1,
           '$2b$12$BohHohN6x7GNNo1KoEnhY.tWHdGbPjRbPica052TsEBZmeOrSbxWC', -- Tester123!
           now() );