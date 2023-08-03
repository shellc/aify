import os
import importlib
from typing import Optional, List

from starlette.authentication import (
    AuthCredentials, AuthenticationBackend, BaseUser
)

from . import _env

class TokenManager:
    def get_token(self):
        raise NotImplementedError()

class LocalTokenManager(TokenManager):
    def __init__(self) -> None:
        super().__init__()
        self._auth_required = True
        self._tokens = {}

        self._load_tokens()

    def get_token(self, token: str):
        return self._tokens.get(token)

    def _load_tokens(self):
        
        tokens_file = os.path.join(_env.apps_dir(), '.tokens')
        if not os.path.exists(tokens_file):
            self._auth_required = False
            return

        with open(tokens_file) as f:
            for line in f.readlines():
                segs = line.split('|')
                token = segs[0].strip()
                if len(token) > 0:
                    self._tokens[token] = {
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
    def __init__(self) -> None:
        super().__init__()

        self._inited = False
        self._auth_required = True
        self._token_manager = None

    def _init(self):
        if 'TOKEN_MANAGER' in os.environ:
            mgr_ref = os.environ['TOKEN_MANAGER']
            idx = mgr_ref.rfind(".")
            pkg_name = mgr_ref[:idx]
            class_name = mgr_ref[idx+1:]

            module = importlib.import_module(pkg_name)
            klass = getattr(module, class_name)
            self._token_manager = klass()
        else:
            self._token_manager = LocalTokenManager()
            self._auth_required = self._token_manager._auth_required

    async def authenticate(self, request):
        if not self._inited:
            self._init()

        if not self._auth_required:
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
            token_stored = self._token_manager.get_token(token)
            if token_stored:
                username = token_stored['username']
                permissions = token_stored['permissions']
                user = AuthenticatedUser(
                    username=username, permissions=permissions)

                scopes = ["authenticated"]
                scopes.extend(permissions)
                credentials = AuthCredentials(scopes=scopes)

                return credentials, user
