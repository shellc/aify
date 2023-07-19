import os
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from ._env import webui_dir

templates = Jinja2Templates(directory=os.path.join(webui_dir(), 'templates'))

def render(template_name, context = {}):
    """Render a template."""
    async def _request(request):
        context['request'] = request
        return templates.TemplateResponse(template_name, context=context)
    return _request