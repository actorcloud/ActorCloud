import os
import sys
from importlib import import_module

from actor_libs.utils import get_services_path


def import_models():
    active_services = get_services_path()
    for key, value in active_services.items():
        schemas_path = os.path.join(value, 'models.py')
        if not os.path.exists(schemas_path):
            continue
        service_path = '.'.join(value.partition('app')[-1].split('/'))
        service_models_path = 'app{0}.models'.format(service_path)
        models_module = import_module(service_models_path)
        service_models = models_module.__all__ if hasattr(models_module, '__all__') else []
        for name, attr in models_module.__dict__.items():
            if name in service_models:
                setattr(sys.modules[__name__], name, attr)


import_models()
