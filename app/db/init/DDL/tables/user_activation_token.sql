CREATE TABLE USER_ACTIVATION_TOKEN (
    USER_ACTIVATION_TOKEN_ID INT PRIMARY KEY,
    USER_ID INT(10),
    USER_ACTIVATION_TOKEN VARCHAR(255),
    USER_ACTIVATION_TOKEN_VALID_FROM DATE,
    USER_ACTIVATION_TOKEN_VALID_TO DATE,
    CREATED_BY VARCHAR(50),
    DATA_INSERTED TIMESTAMP,
    UPDATED_BY VARCHAR(50),
    DATA_UPDATED TIMESTAMP
);

COMMENT ON TABLE USER_ACTIVATION_TOKEN IS 'TABLE HOLDING USER RELATED TOKENS TO ACTIVATE USERS';

CREATE INDEX IDX_UAT_USER_ID ON USER_ACTIVATION_TOKEN (USER_ID);
CREATE INDEX IDX_UAT_UAT_VALID_TO ON USER_ACTIVATION_TOKEN (USER_ACTIVATION_TOKEN_VALID_TO);
