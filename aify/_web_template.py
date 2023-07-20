import os
from starlette.templating import Jinja2Templates
from ._env import webui_dir, apps_dir

templates = Jinja2Templates(directory=os.path.join(webui_dir(), 'templates'))

apps_templates = Jinja2Templates(directory=os.path.join(apps_dir(), 'templates'))

def render(template_name, context = {}, is_apps_tempates=False):
    """Render a template."""
    async def _request(request):
        context['request'] = request
        tpls = apps_templates if is_apps_tempates else templates
        return tpls.TemplateResponse(template_name, context=context)
    return _request

def apps_render(template_name, context = {}):
    return render(template_name=template_name, context=context, is_apps_tempates=True)