from datetime import datetime, date
from typing import List, Optional

from fastapi import Depends, Security, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import SecurityScopes
from jose import JWTError, jwt
from sqlalchemy import func, insert, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import String

import config
from app.api.v1.auth import security
from app.api.v1.auth.oauth2_scheme import OAUTH2_SCHEME
from app.api.v1.auth.schema import ApiUser, TokenData, User, UserInDB
from app.api.v1.auth.security import verify_password
from app.api.v1.schema import HttpError
from app.db.database import get_connection
from app.db.metadata import ApiExpiredTokens, ApiTokens, VwUserGroupRights, VwUserLookup
from app.logging import logger


def get_user(username: str):
    """
    Retrieve a user from the database by username (email).
    
    Args:
        username: The email address of the user to retrieve
        
    Returns:
        UserInDB if found, None otherwise
        
    Raises:
        SQLAlchemyError: If there's a database error
    """
    try:
        with get_connection() as c: 
            query = (
                select(
                    VwUserLookup.c.USER_ID.label("user_id"),
                    # func.replace(cast(VwUserLookup.c.USER_ID, String), '-', '_').label('user_role'),
                    VwUserLookup.c.USER_EMAIL.label("user_role"),
                    VwUserLookup.c.USER_EMAIL.label("username"),
                    VwUserLookup.c.USER_EMAIL.label("email"),
                    VwUserLookup.c.USER_PASSWORD.label("hashed_password"),
                    VwUserLookup.c.USER_VALID_FROM.label("user_registration_timestamp"),
                )
                .where(func.lower(VwUserLookup.c.USER_EMAIL) == func.lower(username))
                .limit(1)
            )

            result = c.execute(query).fetchone()

            if result is None:
                return None
            
            user_data = result._asdict()

            # check if exist and timestamp is an already a datetime.
            if "user_registration_timestamp" in user_data:
                ts = user_data["user_registration_timestamp"]
                if isinstance(ts, datetime):
                    user_data["user_registration_timestamp"] = ts.date()
                elif isinstance(ts, date):
                    # It's already a date — do nothing or reassign as-is
                    user_data["user_registration_timestamp"] = ts

            return UserInDB(**user_data)
    
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_user for username {username}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_user for username {username}: {str(e)}")
        raise


def set_expired_tokens(ivsToken: str) -> None:
    """
    Mark a token as expired in the database.
    
    Args:
        ivsToken: The token to mark as expired
        
    Raises:
        SQLAlchemyError: If there's a database error
    """
    try:
        with get_connection() as c:
            stmt_insert = insert(ApiExpiredTokens).values(
                API_EXPIRED_TOKEN=ivsToken, API_EXPIRED_TOKEN_VALID_FROM=datetime.now()
            )
            c.execute(stmt_insert)
            c.commit()
    except SQLAlchemyError as e:
        logger.info(f"=========================== ERROR {e} ============================")
        logger.error(f"Database error in set_expired_tokens: {str(e)}")
        c.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error in set_expired_tokens: {str(e)}")
        raise



def set_generated_tokens(
    ivsToken: str,
    ivsTokenType: str,
    ivoUser: Optional["User"] = None,
    ivoApiUser: Optional["ApiUser"] = None,
) -> None:
    """
    Store a generated token in the database.
    
    Args:
        ivsToken: The token to store
        ivsTokenType: The type of token
        ivoUser: Optional associated user
        ivoApiUser: Optional associated API user
        
    Raises:
        SQLAlchemyError: If there's a database error
        ValueError: If neither user nor api user is provided
    """
    try:
        with get_connection() as c:
            values_dict = {
                "API_TOKEN": ivsToken,
                "API_TOKEN_TYPE": ivsTokenType,
                "API_TOKEN_VALID_FROM": datetime.now(),
            }

            # Conditional assignments for optional parameters
            if ivoUser is not None:
                values_dict["USER_ID"] = ivoUser.user_id
            if ivoApiUser is not None:
                values_dict["API_USER_ID"] = ivoApiUser.api_user_id

            stmt_insert = insert(ApiTokens).values(**values_dict)
            c.execute(stmt_insert)
            c.commit()

    except SQLAlchemyError as e:
        logger.error(f"Database error in set_generated_tokens: {str(e)}")
        c.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error in set_generated_tokens: {str(e)}")
        raise


def get_expired_tokens(ivsToken: str) -> bool:
    """
    Check if a token is marked as expired in the database.
    
    Args:
        ivsToken: The token to check
        
    Returns:
        bool: True if token is expired, False otherwise
        
    Raises:
        SQLAlchemyError: If there's a database error
    """
    try:
        with get_connection() as c:
            stmt_select = select(
                ApiExpiredTokens.c.API_EXPIRED_TOKEN_ID,
            ).where(ApiExpiredTokens.c.API_EXPIRED_TOKEN == ivsToken)
            result = c.execute(stmt_select).mappings().first()

            return result is not None

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_expired_tokens: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_expired_tokens: {str(e)}")
        raise

def authenticate_user(username: str, password: str):
    """
    Authenticate a user with username and password.
    
    Args:
        username: The user's email/username
        password: The user's password
        
    Returns:
        UserInDB if authentication succeeds, None otherwise
        
    Raises:
        SQLAlchemyError: If there's a database error
    """
    try:
        user = get_user(username)
        logger.info(f"Attempting authentication for user: {username}")

        if not user:
            logger.warning(f"Authentication failed - user not found: {username}")
            return False
        
        # print(f"username = {username}")
        # print(f"password: {password}")
        # print(f"user.hashed_password: {user.hashed_password}")
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed - invalid password for user: {username}")
            return False
            
        logger.info(f"Authentication successful for user: {username}")
        return user
    
    except SQLAlchemyError as e:
        logger.error(f"Database error during authentication for user {username}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during authentication for user {username}: {str(e)}")
        raise


def get_user_scopes(user: UserInDB) -> List[str]:
    """
    Retrieve all scopes/permissions for a given user.
    
    Args:
        user: The user to get scopes for
        
    Returns:
        List of scope strings
        
    Raises:
        SQLAlchemyError: If there's a database error
    """
    defaultScopes = []
    try:
        with get_connection() as connection:
            stmt = select(
                VwUserGroupRights.c.USER_SCOPE_NAME_READ,
                VwUserGroupRights.c.USER_SCOPE_NAME_WRITE,
                VwUserGroupRights.c.USER_SCOPE_NAME_EXECUTE,
                VwUserGroupRights.c.USER_SCOPE_NAME_DELETE,
            ).where(VwUserGroupRights.c.USER_ID == user.user_id)

            result = connection.execute(stmt).fetchall()

            for row in result:
                if row.USER_SCOPE_NAME_READ is not None:
                    defaultScopes.append(row.USER_SCOPE_NAME_READ)
                if row.USER_SCOPE_NAME_WRITE is not None:
                    defaultScopes.append(row.USER_SCOPE_NAME_WRITE)
                if row.USER_SCOPE_NAME_EXECUTE is not None:
                    defaultScopes.append(row.USER_SCOPE_NAME_EXECUTE)
                if row.USER_SCOPE_NAME_DELETE is not None:
                    defaultScopes.append(row.USER_SCOPE_NAME_DELETE)

        return defaultScopes

    except SQLAlchemyError as e:
        logger.error(f"Database error getting scopes for user {user.user_id}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting scopes for user {user.user_id}: {str(e)}")
        raise

async def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(OAUTH2_SCHEME)
):
    """
    Get the current authenticated user from the JWT token.
    
    Args:
        security_scopes: The required security scopes
        token: The JWT token
        
    Returns:
        UserInDB if authentication succeeds, JSONResponse with error otherwise
        
    Raises:
        JWTError: If token validation fails
    """
    try:
        if get_expired_tokens(token):
            raise JWTError
        lcsLocation = "get_curent_user"
        options = {"verify_signature": True, "verify_aud": False, "exp": True}
        payload = jwt.decode(
            token, security.SECRET_KEY, algorithms=[security.ALGORITHM], options=options
        )
        username: str = payload.get("sub")
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
        # for scope in security_scopes.scopes:
        # if scope not in token_data.scopes:
        # raise JWTError
        if username is None:
            raise JWTError
        token_data = TokenData(username=username)
    except JWTError as e:
        logger.error(f"Exception in {lcsLocation}: {e}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(HttpError(message="Permission denied")),
        )
    user = get_user(username=token_data.username)
    logger.error(f"user: {user}")
    if user is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(HttpError(message="Permission denied")),
        )
    return user


async def get_current_active_user(
    current_user: User = Security(get_current_user, scopes=[])
):
    if isinstance(current_user, User):
        if current_user.disabled:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder(HttpError(message="Inactive user")),
            )
    return current_user
