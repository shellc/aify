import os
from typing import Optional, List

from starlette.authentication import (
    AuthCredentials, AuthenticationBackend, BaseUser
)

from . import _env

_auth_required = True
_tokens = {}


def _load_tokens():
    global _auth_required

    tokens_file = os.path.join(_env.apps_dir(), '.tokens')
    if not os.path.exists(tokens_file):
        _auth_required = False
        return

    with open(tokens_file) as f:
        for line in f.readlines():
            segs = line.split('|')
            token = segs[0].strip()
            if len(token) > 0:
                _tokens[token] = {
                    'username': segs[1] if len(segs) > 1 else None,
                    'permissions': [x.strip() for x in segs[2].split(',')] if len(segs) > 2 else []
                }


class AuthenticatedUser(BaseUser):
    def __init__(self, username: Optional[str] = "anonymous", permissions: Optional[List[str]] = []) -> None:
        self._username = username
        self._permissions = permissions

    @property
    def identity(self) -> str:
        return self._username

    @property
    def username(self) -> str:
        return self._username

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def permissions(self) -> Optional[List[str]]:
        return self._permissions


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):

        if len(_tokens) == 0:
            _load_tokens()

        if not _auth_required:
            return AuthCredentials(scopes=['authenticated', 'write']), AuthenticatedUser()

        token = None
        if 'token' in request.query_params:
            token = request.query_params.get('token')

        if not token and "Authorization" in request.headers:
            auth = request.headers["Authorization"]

            scheme, token_str = auth.split()
            if scheme.lower() == 'bearer':
                token = token_str

        if not token:
            token = request.cookies.get('token')

        if token:
            if token in _tokens:
                token_stored = _tokens[token]
                username = token_stored['username']
                permissions = token_stored['permissions']
                user = AuthenticatedUser(
                    username=username, permissions=permissions)

                scopes = ["authenticated"]
                scopes.extend(permissions)
                credentials = AuthCredentials(scopes=scopes)

                return credentials, user
