from fastapi.security import OAuth2PasswordBearer

# NOTE: tokenUrl needs to be an absolute path!
OAUTH2_SCHEME = OAuth2PasswordBearer(
    tokenUrl="/v1/auth/token",
    scopes={
        "Node:Read": "Will be set by group rights",
        "Node:Write": "Will be set by group rights",
        "Node:Execute": "Will be set by group rights",
        "Node:Delete": "Will be set by group rights",
    },
)
