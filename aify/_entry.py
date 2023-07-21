import os
import sys
import json
import importlib
import contextlib
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse, StreamingResponse, RedirectResponse
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import requires
from starlette.exceptions import HTTPException
from fastapi import FastAPI, Request
from . import _env
from . import _program
from . import _auth
from ._logging import logger
from ._web_template import render

# FastAPI
api = FastAPI()

def get_program(name: str) -> _program.Program:
    """A program is an application defined by the user.

    Parameters
    ----------
    name : string
        The name of the program, typically the filename of the user-defined application template.
    """
    program = None
    try:
        program = _program.get(name)
    except Exception as e:
        logger.error(e, exc_info=e)
        raise HTTPException(
            status_code=404, detail=f"Not a valid app: {e}")
    return program

@api.put('/apps/{name}/{session_id}')
@requires(['authenticated', 'write'])
async def execute_program(request: Request, name: str, session_id: str):
    """Execute the program identified by the name."""
    program = get_program(name)
    
    kwargs = {}
    try:
        kwargs = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Bad request body.")
    
    kwargs['program_name'] = name
    kwargs['session_id'] = session_id

    filter_variable = request.query_params.get('variable')
    if filter_variable and not (filter_variable in program.input_variable_names or filter_variable in program.output_variable_names):
        raise HTTPException(status_code=400, detail="invalid variable.")

    # Check if the Server-Sent Event enabled.
    sse = 'sse' in request.query_params

    # https://github.com/microsoft/guidance/discussions/129
    async def _aiter():
        pos = dict([(vname, 0) for vname in program.output_variable_names])
        catched = False

        kwargs['stream'] = True
        kwargs['async_mode'] = True
        kwargs['silent'] = True

        async for t in program.run(**kwargs):
            if t._exception:
                if catched:
                    return
                catched = True

                e = {
                    "error": str(t._exception)
                }
                if sse:
                    yield "event: error\ndata: %s\n\n" % json.dumps(e)
                else:
                    yield json.dumps(e)
            else:
                for vname in program.output_variable_names:

                    if filter_variable and vname != filter_variable:
                        continue

                    generated = t.get(vname)
                    if generated:
                        diff = generated[pos[vname]:]
                        pos[vname] = len(generated)
                        if len(diff) > 0:
                            if sse:
                                e = {
                                    "variable": vname,
                                    "diff": diff
                                }

                                yield "event: message\ndata: %s\n\n" % json.dumps(e)
                            else:
                                yield diff

    content_type = 'text/event-stream' if sse else 'text/plain'

    try:
        it = _aiter()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Something wrong: {e}")

    return StreamingResponse(it, headers={'Content-Type': content_type})

@api.get('/apps/{name}/{session_id}/memories')
@requires(['authenticated'])
async def get_memories(request: Request, name: str, session_id: str, limit=1000):
    """Get the memory content of the specified application's current session."""
    memories = []
    program = get_program(name)
    memory = program.modules.get('memory')
    if memory:
        m = memory.read(name, session_id, max_len=2040*1024, n=limit)
        if m:
            memories = m
    return JSONResponse(memories)

@api.get('/apps')
@requires(['authenticated'])
async def list_apps(request: Request):
    """List applications"""
    progs = []
    if len(_program.programs) == 0:
        _program.reload(skip_error=True)

    for name, prog in _program.programs.items():
        progs.append({
            'name': name,
            'title': prog.template.get('title'),
            'description': prog.template.get('description'),
            'icon_emoji': prog.template.get('icon_emoji'),
        })
    
    return JSONResponse(progs)

@api.get('/sessions')
@requires(['authenticated'])
async def list_sessions(request: Request):
    """List sessions"""
    
    sessions = []

    progs = []
    if len(_program.programs) == 0:
        _program.reload(skip_error=True)

    for name, prog in _program.programs.items():
        memory = prog.modules.get('memory')
        sessions.extend(memory.sessions(name))

    sessions = sorted(sessions, key=lambda x: x.get('last_modified'), reverse=True)

    return JSONResponse(sessions)

async def auth(request: Request):
    response = await render('auth.html')(request=request)
    if request.method == 'POST':
        next = request.query_params.get('next')
        if next:
            response = RedirectResponse(next, status_code=302)
        
        async with request.form() as form:
            token = form.get('token')
            response.set_cookie('token', token, max_age=7*24*3600)
    return response

@api.get('/user')
@requires(['authenticated'])
async def get_user(request: Request):
    user = {
        'username': request.user.username,
        "permissions": request.user.permissions
    }
    return JSONResponse(user)

# Routes
routes = [
    Mount(
        '/api',
        name='api',
        app=api
    ),
    Mount(
        '/static',
        name='static',
        app=StaticFiles(directory=os.path.join(_env.webui_dir(), 'static'), check_dir=False),
    ),
    Route(
        '/',
        name='home',
        endpoint=requires(scopes=['authenticated'], redirect='auth')(render('index.html'))
    ),
    Route(
        '/auth',
        name='auth',
        methods=['POST', 'GET'],
        endpoint=auth
    )
]

apps_static_dir = os.path.join(_env.apps_dir(), 'static')
if os.path.exists(apps_static_dir):
    routes.append(Mount(
        '/apps/static',
        name='apps_static',
        app=StaticFiles(directory=apps_static_dir, check_dir=False),
    ))

# Middlewares
middleware = [
    Middleware(AuthenticationMiddleware, backend=_auth.BasicAuthBackend())
]

def import_entry():
    sys.path.append(_env.apps_dir())
    entry_py = os.path.join(_env.apps_dir(), 'entry.py')
    if os.path.exists(entry_py):
        importlib.import_module('entry')

@contextlib.asynccontextmanager
async def lifespan(app):
    import_entry()
    yield

entry = Starlette(debug=True, routes=routes, middleware=middleware, lifespan=lifespan)

env_file = os.path.join(_env.apps_dir(), '.env')
if os.path.exists(env_file):
        from dotenv import load_dotenv
        load_dotenv(env_file)