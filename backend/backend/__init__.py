"""Django project package initialization."""

import sys
from importlib import util
from pathlib import Path

# Ensure the Django app living at ``backend/inventory`` can be imported via both
# ``backend.inventory`` and ``inventory`` regardless of the current working
# directory. This mirrors the project layout expected by the tests.
if 'backend.inventory' not in sys.modules:
    inventory_path = Path(__file__).resolve().parent.parent / 'inventory'
    spec = util.spec_from_file_location(
        'backend.inventory',
        inventory_path / '__init__.py',
        submodule_search_locations=[str(inventory_path)],
    )
    module = util.module_from_spec(spec)
    sys.modules['backend.inventory'] = module
    sys.modules.setdefault('inventory', module)
    assert spec.loader is not None
    spec.loader.exec_module(module)
