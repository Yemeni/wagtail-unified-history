from types import SimpleNamespace
from importlib import import_module

wagtail_hooks = import_module("wagtail_unified_history.wagtail_hooks")


def test_menu_item_visibility_and_url(monkeypatch):
    item = wagtail_hooks.MergedHistoryMenuItem(order=90)

    assert item.is_shown({"page": object()}) is True
    assert item.is_shown({}) is False

    context = {"page": SimpleNamespace(id=5)}
    monkeypatch.setattr(wagtail_hooks, "reverse", lambda name, args: f"/pages/{args[0]}/")
    assert item.get_url(context) == "/pages/5/"
    assert wagtail_hooks.register_merged_history_item().name == "merged_history"


