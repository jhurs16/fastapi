from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
)
from sqlalchemy.dialects.mysql import LONGTEXT, DATE, INTEGER, VARCHAR

_meta = MetaData()

VwUserGroupRights = Table(
    "VW_USER_GROUP_RIGHTS",
    _meta,
    Column("USER_GROUP_NAME", VARCHAR(255)),
    Column("USER_OBJECT_NAME", VARCHAR(255)),
    Column("USER_OBJECT_URL", VARCHAR(255)),
    Column("USER_SCOPE_NAME_READ", VARCHAR(255)),
    Column("USER_SCOPE_NAME_WRITE", VARCHAR(255)),
    Column("USER_SCOPE_NAME_EXECUTE", VARCHAR(255)),
    Column("USER_SCOPE_NAME_DELETE", VARCHAR(255)),
    Column("USER_ID", INTEGER),
    Column("API_USER_ID", INTEGER),
    Column("API_CLIENT_ID", INTEGER),
    Column("USER_GROUP_RIGHT_ID", INTEGER, primary_key=True),
    Column("USER_GROUP_ID", INTEGER, ForeignKey("USER_GROUPS.USER_GROUP_ID")),
    Column("USER_OBJECT_ID", INTEGER, ForeignKey("USER_OBJECTS.USER_OBJECT_ID")),
    Column("USER_GROUP_RIGHT_READ", VARCHAR(1)),
    Column("USER_GROUP_RIGHT_WRITE", VARCHAR(1)),
    Column("USER_GROUP_RIGHT_EXECUTE", VARCHAR(1)),
    Column("USER_GROUP_RIGHT_DELETE", VARCHAR(1)),
    Column("USER_GROUP_RIGHT_VALID_FROM", DATE),
)

ApiTokens = Table(
    "API_TOKENS",
    _meta,
    Column("API_TOKEN_ID", Integer, primary_key=True),
    Column("API_TOKEN", String(2000)),
    Column("USER_ID", INTEGER, nullable=True),
    Column("API_CLIENT_ID", INTEGER, nullable=True),
    Column("API_USER_ID", INTEGER, nullable=True),
    Column("API_TOKEN_TYPE", String(255)),
    Column("API_TOKEN_VALID_FROM", Date),
    Column("API_TOKEN_VALID_TO", Date),
    Column("CREATED_BY", String(50)),
    Column("DATA_INSERTED", DateTime),
    Column("UPDATED_BY", String(50)),
    Column("DATA_UPDATED", DateTime),
)

# vw_user_lookup View Definition
VwUserLookup = Table(
    "VW_USER_LOOKUP",
    _meta,
    Column("USER_ID", String(36), primary_key=True),
    Column("USER_PARENT_ID", String(36)),
    Column("USER_NAME", String(255)),
    Column("USER_EMAIL", String(255)),
    Column("USER_VALID_FROM", Date),
    Column("USER_DETAILS_ID", Integer),
    Column("USER_PASSWORD", String(255)),
    Column("USER_DETAILS_SALUTATION", String(50)),
    Column("USER_DETAILS_FIRSTNAME", String(100)),
    Column("USER_DETAILS_LASTNAME", String(100)),
    Column("USER_DETAILS_COMPANY", String(100)),
    Column("USER_DETAILS_BIRTHDAY", Date),
    Column("USER_DETAILS_GENDER", String(30)),
    Column("USER_DETAILS_PHONE", String(40)),
    Column("USER_DETAILS_FAX", String(40)),
    Column("USER_DETAILS_MOBILE", String(40)),
    Column("USER_DETAILS_MOBILE_NOTIFICATION", String(1)),
    Column("USER_DETAILS_EMAIL", String(255)),
    Column("USER_DETAILS_EMAIL_NOTIFICATION", String(1)),
    Column("USER_DETAILS_PREFERRED_LANGUAGE", String(2)),
)


# API_EXPIRED_TOKENS Table Definition
ApiExpiredTokens = Table(
    "API_EXPIRED_TOKENS",
    _meta,
    Column("API_EXPIRED_TOKEN_ID", Integer, primary_key=True),
    Column("API_EXPIRED_TOKEN", String(4000)),
    Column("API_EXPIRED_TOKEN_VALID_FROM", Date),
    Column("API_EXPIRED_TOKEN_VALID_TO", Date),
    Column("CREATED_BY", String(50)),
    Column("DATA_INSERTED", DateTime),
    Column("UPDATED_BY", String(50)),
    Column("DATA_UPDATED", DateTime),
)


def get_metadata() -> MetaData:
    global _meta
    return _meta