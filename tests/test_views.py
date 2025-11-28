from types import SimpleNamespace
from datetime import datetime

from importlib import import_module

views = import_module("wagtail_unified_history.views")


class DummyFilterSet:
    def __init__(self, data=None, queryset=None, valid=True):
        self.data = data
        self.queryset = queryset
        self._valid = valid
        self.form = SimpleNamespace(cleaned_data={"user": [], "action": []})

    def is_valid(self):
        return self._valid


def test_merged_history_view_filters_and_templates(monkeypatch):
    root_page = SimpleNamespace(id=1, path="/home/")
    desc_page = SimpleNamespace(id=2, path="/home/child/")

    def fake_get_object_or_404(model, id):
        assert id == 1
        return root_page

    class FakePageManager:
        def filter(self, **kwargs):
            return SimpleNamespace(values_list=lambda *a, **k: [1, 2])

    class FakePageLogEntryManager:
        def filter(self, **kwargs):
            assert kwargs["page_id__in"] == [1, 2]
            return "log_qs"

    entries = [
        {"id": 1, "timestamp": datetime(2024, 2, 1, 10), "user_id": 1, "action": "keep"},
        {"id": 2, "timestamp": datetime(2024, 2, 2, 10), "user_id": 2, "action": "remove"},
    ]

    def fake_get_merged_history_qs(page, filters=None):
        assert filters["date_from"].year == 2024
        assert filters["date_to"].year == 2024
        return entries

    def fake_render(request, template_name, context):
        return template_name, context

    request = SimpleNamespace(
        GET={
            "user": "1",
            "timestamp_from": "2024-02-01",
            "timestamp_to": "2024-02-02",
            "p": "1",
        },
        headers={},
    )

    monkeypatch.setattr(views, "get_object_or_404", fake_get_object_or_404)
    monkeypatch.setattr(views.Page, "objects", FakePageManager())
    monkeypatch.setattr(views.PageLogEntry, "objects", FakePageLogEntryManager())
    monkeypatch.setattr(views, "HistoryFilterSet", lambda *a, **k: DummyFilterSet())
    monkeypatch.setattr(views, "get_merged_history_qs", fake_get_merged_history_qs)
    monkeypatch.setattr(views, "render", fake_render)

    template_name, context = views.merged_history_view(request, 1)

    assert template_name == "wagtail_unified_history/merged_history.html"
    assert context["root_page"] is root_page
    assert list(context["entries"])[0]["id"] == 1


def test_merged_history_view_partial_template(monkeypatch):
    request = SimpleNamespace(
        GET={},
        headers={"HX-Target": "listing-results"},
    )
    root_page = SimpleNamespace(id=9, path="/root/")

    monkeypatch.setattr(views, "get_object_or_404", lambda *a, **k: root_page)
    monkeypatch.setattr(views.Page, "objects", SimpleNamespace(filter=lambda **k: SimpleNamespace(values_list=lambda *a, **kw: [])))
    monkeypatch.setattr(views.PageLogEntry, "objects", SimpleNamespace(filter=lambda **k: "qs"))
    monkeypatch.setattr(views, "HistoryFilterSet", lambda *a, **k: DummyFilterSet())
    monkeypatch.setattr(views, "get_merged_history_qs", lambda *a, **k: [])
    monkeypatch.setattr(views, "render", lambda request, template, context: (template, context))

    template_name, _ = views.merged_history_view(request, 9)
    assert template_name == "wagtail_unified_history/includes/merged_history_results.html"
