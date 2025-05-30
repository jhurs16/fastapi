CREATE TABLE USER_OBJECTS (
    USER_OBJECT_ID INT(10) PRIMARY KEY,
    USER_OBJECT_PARENT_ID INT(10),
    USER_OBJECT_NAME VARCHAR(100),
    USER_OBJECT_URL VARCHAR(255),
    USER_OBJECT_VALID_FROM DATE,
    USER_OBJECT_VALID_TO DATE,
    CREATED_BY VARCHAR(50),
    DATA_INSERTED TIMESTAMP,
    UPDATED_BY VARCHAR(50),
    DATA_UPDATED TIMESTAMP
);

COMMENT ON TABLE USER_OBJECTS IS 'TABLE HOLDING INFORMATION ABOUT GENERIC OBJECTS TO BE GRANTED TO USER_GROUPS';

CREATE INDEX IDX_USER_OBJECTS_USER_OBJECT_PARENT_ID ON USER_OBJECTS (USER_OBJECT_PARENT_ID);
CREATE INDEX IDX_USER_OBJECTS_USER_OBJECT_VALID_TO ON USER_OBJECTS (USER_OBJECT_VALID_TO);