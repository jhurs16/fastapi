from datetime import datetime, timedelta

import jwt

from fastapi import APIRouter, Depends, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse 
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError

from app.api.v1.auth import access, security
from app.api.v1.auth.oauth2_scheme import OAUTH2_SCHEME
from app.api.v1.auth.schema import LogoutResponse, Token, TokenValidationResponse
from app.api.v1.schema import HttpError
from app.logging import logger

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/token",
    response_model=Token,
)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    access_token = None
    refresh_token = None
    scopes = None

    try:
        
        user = access.authenticate_user(form_data.username, form_data.password)
        user_id = None
        logger.info(f"user=> {user}, form_data=> {form_data.__dict__}")
        if user:
            scopes = access.get_user_scopes(user)
        if scopes is None:
            scopes = []
        if user:
            user_id = user.user_id
            access_token_expires = timedelta(
                minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            access_token = security.create_access_token(
                data={
                    "sub": user.username,
                    "aud": "user_context",
                    "scopes": scopes,
                    "type": "access",
                    "registration_timestamp": datetime.utcnow().timestamp(),
                },
                expires_delta=access_token_expires,
            )
            access.set_generated_tokens(
                ivsToken=access_token,
                ivoUser=user,
                ivsTokenType="access",
            )
            refresh_token_expires = timedelta(
                minutes=security.REFRESH_TOKEN_EXPIRE_MINUTES
            )
            refresh_token = security.create_access_token(
                data={"sub": user.username, "aud": "user_context", "type": "refresh"},
                expires_delta=refresh_token_expires,
            )
            access.set_generated_tokens(
                ivsToken=refresh_token, ivoUser=user, ivsTokenType="refresh"
            )
        else:
            raise JWTError
    except JWTError:
      
        
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(HttpError(message="Permission denied default high")),
        )
    return Token(
        user_id=user_id,
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
    )


@router.post(
    "/token/refresh/{refresh_token}",
    response_model=Token,
)
async def refresh_token(refresh_token: str):
    try:
        lcsLocation = "[POST]token/refresh/"
        access_token = None
        options = {"verify_signature": True, "verify_aud": False, "exp": True}
        payload = jwt.decode(
            refresh_token,
            security.SECRET_KEY,
            algorithms=[security.ALGORITHM],
            options=options,
        )
        audience: str = payload.get("aud")
        username: str = payload.get("sub")
        if username is None:
            raise JWTError
        user = access.get_user(username)
        if audience == "user_context" and user:
            scopes = access.get_user_scopes(user)
            access_token_expires = timedelta(
                minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            access_token = security.create_access_token(
                data={
                    "sub": user.username,
                    "aud": "user_context",
                    "scopes": scopes,
                },
                expires_delta=access_token_expires,
            )
            refresh_token_expires = timedelta(
                minutes=security.REFRESH_TOKEN_EXPIRE_MINUTES
            )
            refresh_token = security.create_access_token(
                data={
                    "sub": user.username,
                    "aud": "user_context",
                },
                expires_delta=refresh_token_expires,
            )
        if audience == "machine_context" and user is None:
            client = access.get_client(username)
            if client is None:
                raise JWTError
            scopes = access.get_client_scopes(client)
            access_token_expires = timedelta(
                minutes=security.gcnAccessTokenClientExpiration
            )
            access_token = security.create_access_token(
                data={
                    "sub": client.client_id,
                    "aud": "machine_context",
                    "scopes": scopes,
                },
                expires_delta=access_token_expires,
            )
            refresh_token_expires = timedelta(
                minutes=security.REFRESH_TOKEN_EXPIRE_MINUTES
            )
            refresh_token = security.create_access_token(
                data={
                    "sub": client.client_id,
                    "aud": "machine_context",
                },
                expires_delta=refresh_token_expires,
            )
    except JWTError as e:
        logger.error(f"Exception in {lcsLocation}: {e}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=jsonable_encoder(HttpError(message="Permission denied default low")),
        )

    return Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
    )


@router.post(
    "/token/validate",
    response_model=TokenValidationResponse,
)
async def validate_token(token: str):
    try:
        lcsLocation = "[POST]token/validate"
        validated_token = TokenValidationResponse(
            data=None,
            message="Your token could not be validated",
            status=status.HTTP_404_NOT_FOUND,
            success=False,
        )
        options = {"verify_signature": True, "verify_aud": False, "exp": True}
        payload = jwt.decode(
            token,
            security.SECRET_KEY,
            algorithms=[security.ALGORITHM],
            options=options,
        )
        audience: str = payload.get("aud")
        username: str = payload.get("sub")
        if username is None:
            raise JWTError
        user = access.get_user(username)
        if audience == "user_context" and user:
            validated_token = TokenValidationResponse(
                data=None,
                message="Your token is valid.",
                status=status.HTTP_200_OK,
                success=True,
            )
        if audience == "machine_context" and user is None:
            client = access.get_client(username)
            if client is None:
                raise JWTError
            else:
                validated_token = TokenValidationResponse(
                    data=None,
                    message="Your token is valid.",
                    status=status.HTTP_200_OK,
                    success=True,
                )
    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(validated_token),
        )
    except JWTError as e:
        logger.error(f"Exception in {lcsLocation}: {e}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=jsonable_encoder(validated_token),
        )

    return validated_token


@router.post(
    "/token/logout",
    response_model=LogoutResponse,
)
async def logout_token(
    request: Request,
    token: str = Depends(OAUTH2_SCHEME),
):
    try:
        lcsLocation = "[POST]token/logout/"
        access.set_expired_tokens(token)
        lvjLogoutResponse = LogoutResponse(
            data="",
            message="User has been logged out",
            status=status.HTTP_200_OK,
            success=True,
        )
        # logger.info(f"------------ try lcsLocation {lcsLocation}-------------")
        # logger.info(f"------------ try access.set_expired_tokens(token) {access.set_expired_tokens(token)}-------------")
        # logger.info(f"------------ try lvjLogoutResponse {lvjLogoutResponse}-------------")
        
    except Exception as e:
        logger.error(f"Exception in {lcsLocation}: {e}")
        logger.info(f"###logout token### -- {token}--")
    
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                HttpError(message="Could not log out / invalidate user/token")
            ),
        )

    return lvjLogoutResponse
