import os
import sys
import glob
import yaml
import importlib
from string import Template
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except:
    from yaml import Loader, Dumper

import guidance

from . import _env
from ._error import AifyError
from ._logging import logger


class CompileError(AifyError):
    pass


class Program:
    """
    The Program class represents an executable program driven by a LLM.
    """

    def __init__(self, template: str) -> None:
        self._template = None
        self._runner = None
        self._modules = {}
        self._input_variables = []
        self._output_variables = []

        try:
            self._compile(template=template)
        except Exception as e:
            raise CompileError(e)

    def _compile(self, template: str):
        try:
            # replace env variables
            t = Template(template=template)
            t = t.substitute(os.environ)
            self._template = yaml.load(t, Loader=Loader)
        except Exception as e:
            raise ValueError(f"parse template faild, {e}")

        model = None
        model_settings = self._template.get('model')
        if not model_settings:
            raise ValueError("missing model section in the template.")

        model_name = model_settings.get('name')
        if not model_name:
            raise ValueError("missing model name.")

        model_params = model_settings.get('params', {})

        if 'type' not in model_settings or model_settings['type'] == 'llm':
            if model_settings['vendor'].lower() == 'openai':
                model = guidance.llms.OpenAI(model_name, **model_params)
            else:
                raise ValueError(
                    f"the model vendor `{model_settings['vendor']}` is not support yet.")
        else:
            raise ValueError(
                f"the model type `{model_settings['type']}` is not support yet.")

        prompt = self._template.get('prompt')
        if not prompt or not isinstance(prompt, str):
            raise ValueError("missing prompt text.")

        self._runner = guidance(prompt, llm=model, silent=True)

        self._import_modules()

        variables = self._template.get('variables', [])
        for var in variables:
            name = var.get('name')
            if not name or not isinstance(name, str):
                raise ValueError(f'invalid variable')
            typ = var.get('type')
            if not typ or typ == 'output':
                self._output_variables.append(var)
            else:
                self._input_variables.append(var)

    def _import_modules(self):
        module_names = self.template.get("modules", {})
        for name, module_name in module_names.items():
            try:
                module = importlib.import_module(module_name)
                self._modules[name] = module
            except Exception as e:
                raise ValueError(f"moudle `{module_name}` not found")

        if 'memory' not in self._modules:
            import aify.memory
            self._modules['memory'] = aify.memory

        if 'embeddings' not in self._modules:
            import aify.embeddings
            self._modules['embeddings'] = aify.embeddings

    def run(self, **kwargs):
        """Run this program."""
        kwargs.update(self._modules)
        return self._runner(**kwargs)

    @property
    def modules(self):
        return self._modules

    @property
    def template(self):
        return self._template

    @property
    def input_variable_names(self):
        return [x['name'] for x in self._input_variables]

    @property
    def output_variable_names(self):
        return [x['name'] for x in self._output_variables]


def _load_template(url: str):
    template = None
    if url.startswith("http://") or url.startswith("https://"):
        pass
    else:
        with open(url) as f:
            template = f.read()

    return template


programs = {}


def reload(apps_dir: str = None, skip_error=False):
    """Load programs from the user's application directory."""
    global programs

    if not apps_dir:
        apps_dir = _env.apps_dir()

    sys.path.append(apps_dir)

    exts = ['*.yml', '*.yaml']
    files = []
    for e in exts:
        files.extend(glob.glob(os.path.join(apps_dir, e)))
    for f in files:
        template = _load_template(f)
        try:
            program = Program(template=template)
        except Exception as e:
            if not skip_error:
                raise e
            else:
                logger.warn(f"Compile program error: {e}")

        programs[os.path.basename(f).split('.')[0]] = program
    return programs


def get(name: str):
    """Retrieve a specific program from the user's application directory."""
    global programs
    if name not in programs:
        apps_dir = _env.apps_dir()
        if os.path.exists(os.path.join(apps_dir, f'{name}.yml')) or os.path.exists(os.path.join(apps_dir, f'{name}.yaml')):
            reload(skip_error=True)

    return programs.get(name)
