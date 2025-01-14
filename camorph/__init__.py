import importlib
import os
import pkgutil
import sys
import pathlib

basepath = pathlib.Path(__file__).parent.resolve()
extpath = os.path.join(basepath, 'ext')
sys.path.append(extpath)
sys.path.append(str(basepath))
crucial_property_config = None
imported_instances = {}
for module in pkgutil.iter_modules([extpath]):
    imported_module = importlib.import_module(module.name)
    # need to disable IDE inspection as PyCharm cannot resolve dynamically imported method
    # noinspection PyUnresolvedReferences
    imported_instance = \
        imported_module.camorph_extension()
    imported_instances[imported_instance.name().lower()] = imported_instance
