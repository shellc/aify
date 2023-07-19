import os

_here = os.path.abspath(os.path.join(os.path.dirname(__file__)))


def apps_dir():
    """Returns the directory where user applications are stored."""
    apps_dir = os.environ['AIFY_APPS_DIR'] if 'AIFY_APPS_DIR' in os.environ else None
    return apps_dir if apps_dir else '.'


def webui_dir():
    "Returns the directory where webuid resources ared stored."
    return os.path.join(_here, '../webui')
