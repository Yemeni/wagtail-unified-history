import sys
import types
from types import SimpleNamespace

# Ensure repository root on path and expose a package alias for imports
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

package_mod = types.ModuleType("wagtail_unified_history")
package_mod.__path__ = [str(ROOT)]
sys.modules.setdefault("wagtail_unified_history", package_mod)

# ----- Django stubs -----
django = types.ModuleType("django")
sys.modules.setdefault("django", django)

# django.db.models
models_mod = types.ModuleType("django.db.models")

class F:
    def __init__(self, name):
        self.name = name

class Value:
    def __init__(self, value, output_field=None):
        self.value = value
        self.output_field = output_field

class CharField:
    pass

models_mod.F = F
models_mod.Value = Value
models_mod.CharField = CharField

db_mod = types.ModuleType("django.db")
db_mod.models = models_mod

sys.modules.setdefault("django.db", db_mod)
sys.modules.setdefault("django.db.models", models_mod)

# django.apps
apps_mod = types.ModuleType("django.apps")

class AppConfig:
    pass

apps_mod.AppConfig = AppConfig
sys.modules.setdefault("django.apps", apps_mod)

# django.contrib.contenttypes.models
ct_mod = types.ModuleType("django.contrib.contenttypes.models")
ct_mod.ContentType = SimpleNamespace
sys.modules.setdefault("django.contrib", types.ModuleType("django.contrib"))
sys.modules.setdefault("django.contrib.contenttypes", types.ModuleType("django.contrib.contenttypes"))
sys.modules.setdefault("django.contrib.contenttypes.models", ct_mod)

# django.utils.safestring
safestring_mod = types.ModuleType("django.utils.safestring")
safestring_mod.mark_safe = lambda value: value
sys.modules.setdefault("django.utils", types.ModuleType("django.utils"))
sys.modules.setdefault("django.utils.safestring", safestring_mod)

# django.shortcuts
shortcuts_mod = types.ModuleType("django.shortcuts")
shortcuts_mod.get_object_or_404 = lambda model, id: None
shortcuts_mod.render = lambda request, template_name, context: (template_name, context)
sys.modules.setdefault("django.shortcuts", shortcuts_mod)

# django.core.paginator
paginator_mod = types.ModuleType("django.core.paginator")

class Paginator:
    def __init__(self, items, per_page):
        self.items = items
        self.per_page = per_page

    def get_page(self, number):
        return self.items

paginator_mod.Paginator = Paginator
sys.modules.setdefault("django.core", types.ModuleType("django.core"))
sys.modules.setdefault("django.core.paginator", paginator_mod)

# django.urls
urls_mod = types.ModuleType("django.urls")
urls_mod.reverse = lambda name, args=None: f"/reverse/{name}/{'/'.join(str(a) for a in (args or []))}"
urls_mod.path = lambda route, view, name=None: (route, view, name)
sys.modules.setdefault("django.urls", urls_mod)

# ----- Wagtail stubs -----
wagtail_mod = types.ModuleType("wagtail")
sys.modules.setdefault("wagtail", wagtail_mod)

# wagtail.models
wagtail_models = types.ModuleType("wagtail.models")
class Page:
    objects = None

    @classmethod
    def __subclasses__(cls):
        return []

class PageLogEntry:
    objects = None

class Revision:
    objects = None

wagtail_models.Page = Page
wagtail_models.PageLogEntry = PageLogEntry
wagtail_models.Revision = Revision
sys.modules.setdefault("wagtail.models", wagtail_models)

# wagtail.admin.views.generic.history
history_mod = types.ModuleType("wagtail.admin.views.generic.history")
history_mod.HistoryFilterSet = lambda *a, **k: None
sys.modules.setdefault("wagtail.admin", types.ModuleType("wagtail.admin"))
sys.modules.setdefault("wagtail.admin.views", types.ModuleType("wagtail.admin.views"))
sys.modules.setdefault("wagtail.admin.views.generic", types.ModuleType("wagtail.admin.views.generic"))
sys.modules.setdefault("wagtail.admin.views.generic.history", history_mod)

# wagtail.log_actions
log_actions_mod = types.ModuleType("wagtail.log_actions")
log_actions_mod.registry = SimpleNamespace(has_scanned_for_actions=True, scan_for_actions=lambda: None)
sys.modules.setdefault("wagtail.log_actions", log_actions_mod)

# ----- Wagtail admin action menu stubs -----
action_menu_mod = types.ModuleType("wagtail.admin.action_menu")
class ActionMenuItem:
    def __init__(self, order=None):
        self.order = order

action_menu_mod.ActionMenuItem = ActionMenuItem
sys.modules.setdefault("wagtail.admin.action_menu", action_menu_mod)

# ----- Wagtail hooks -----
hooks_mod = types.ModuleType("wagtail.hooks")
hooks_mod.register = lambda name: (lambda func: func)
sys.modules.setdefault("wagtail.hooks", hooks_mod)
