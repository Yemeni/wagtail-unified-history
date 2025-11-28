from types import SimpleNamespace
from datetime import datetime, date
from django.db.models import F, Value, CharField

from wagtail_unified_history import queries


class FakeQuerySet:
    def __init__(self, items):
        self.items = items

    def values_list(self, *fields, flat=False):
        if flat:
            field = fields[0]
            return [getattr(item, field) for item in self.items]
        return [tuple(getattr(item, f) for f in fields) for item in self.items]


class FakePage(SimpleNamespace):
    _meta = SimpleNamespace(abstract=False)

    @classmethod
    def __subclasses__(cls):
        return [cls]


class FakePageManager:
    def __init__(self, pages):
        self.pages = pages

    def filter(self, **kwargs):
        if "path__startswith" in kwargs:
            path = kwargs["path__startswith"]
            return FakeQuerySet([p for p in self.pages if p.path.startswith(path)])
        if "id__in" in kwargs:
            ids = set(kwargs["id__in"])
            return FakeQuerySet([p for p in self.pages if p.id in ids])
        return FakeQuerySet(self.pages)

    def get(self, pk):
        for page in self.pages:
            if page.id == pk:
                return page
        raise LookupError("Page not found")

    def values_list(self, *args, **kwargs):
        return []


class FakePageLogEntry(SimpleNamespace):
    pass


class FakePageLogEntryManager:
    def __init__(self, entries):
        self.entries = entries

    def filter(self, **kwargs):
        page_ids = kwargs.get("page_id__in", [])
        filtered = [e for e in self.entries if e.page_id in page_ids]
        return FakeLogQuerySet(filtered)


class FakeLogQuerySet:
    def __init__(self, entries):
        self.entries = entries

    def select_related(self, *args):
        return self

    def order_by(self, *args):
        return self.entries


class FakeRevision(SimpleNamespace):
    pass


class FakeRevisionManager:
    def __init__(self, revisions):
        self.revisions = revisions

    def filter(self, **kwargs):
        filtered = self.revisions
        if "content_type_id__in" in kwargs:
            allowed = set(kwargs["content_type_id__in"])
            filtered = [r for r in filtered if r.content_type_id in allowed]
        if "object_id__in" in kwargs:
            allowed = set(kwargs["object_id__in"])
            filtered = [r for r in filtered if r.object_id in allowed]
        return FakeRevisionManager(filtered)

    def select_related(self, *args):
        return self

    def annotate(self, **kwargs):
        annotated = []
        for rev in self.revisions:
            data = rev.__dict__.copy()
            for key, expression in kwargs.items():
                if isinstance(expression, F):
                    data[key] = data[expression.name]
                elif isinstance(expression, Value):
                    data[key] = expression.value
                else:
                    data[key] = expression
            annotated.append(SimpleNamespace(**data))
        return FakeAnnotatedRevisions(annotated)


class FakeAnnotatedRevisions:
    def __init__(self, revisions):
        self.revisions = revisions

    def values(self, *fields):
        return [
            {field: getattr(rev, field) for field in fields}
            for rev in self.revisions
        ]


class FakeRegistry:
    def __init__(self):
        self.has_scanned_for_actions = False
        self.scan_called = 0

    def scan_for_actions(self):
        self.has_scanned_for_actions = True
        self.scan_called += 1


class FakeContentType:
    def __init__(self, mapping):
        self.mapping = mapping

    def get_for_model(self, model):
        return SimpleNamespace(id=self.mapping.get(model, 0))


class FakeFormatter:
    def __init__(self, text):
        self.text = text

    def format_message(self, entry):
        if getattr(entry, "boom", False):
            raise RuntimeError("formatting error")
        return self.text


# Ensure patched modules

def setup_module(module):
    pages = [
        FakePage(id=1, path="/home/", title="Home"),
        FakePage(id=2, path="/home/child/", title="Child"),
    ]
    revisions = [
        FakeRevision(id=3, created_at=datetime(2024, 1, 1, 12), user_id=2, user__username="rev_user", content_type_id=10, object_id=1),
        FakeRevision(id=4, created_at=datetime(2024, 1, 2, 12), user_id=3, user__username="rev_user2", content_type_id=10, object_id=2),
    ]
    log_entries = [
        FakePageLogEntry(
            id=5,
            timestamp=datetime(2024, 2, 1, 10),
            user=SimpleNamespace(username="log_user"),
            user_id=2,
            page_id=2,
            page=pages[1],
            action="wagtail.publish",
            message="published",
            formatter=FakeFormatter("Formatted publish"),
        ),
        FakePageLogEntry(
            id=6,
            timestamp=datetime(2024, 2, 2, 10),
            user=SimpleNamespace(username="log_user2"),
            user_id=3,
            page_id=1,
            page=pages[0],
            action="wagtail.edit",
            message="edited",
            formatter=FakeFormatter("Formatted edit"),
            boom=True,
        ),
    ]

    queries.Page = FakePage
    queries.ContentType = SimpleNamespace(objects=FakeContentType({FakePage: 10}))
    queries.Revision = SimpleNamespace(objects=FakeRevisionManager(revisions))
    queries.PageLogEntry = SimpleNamespace(objects=FakePageLogEntryManager(log_entries))
    queries.registry = FakeRegistry()
    queries.Page.objects = FakePageManager(pages)


def test_get_merged_history_qs_merges_and_formats():
    result = queries.get_merged_history_qs(1)

    assert [item["id"] for item in result] == [6, 5, 4, 3]
    log_entry = result[1]
    assert log_entry["message"] == "Formatted publish"
    assert log_entry["entry_type"] == "log"

    revision_entry = result[-1]
    assert revision_entry["message"] == "Revision saved"
    assert revision_entry["page__title"] == "Home"
    assert queries.registry.has_scanned_for_actions is True
    assert queries.registry.scan_called == 1


def test_get_merged_history_qs_applies_filters_and_defaults():
    filters = {
        "user_id": 3,
        "date_from": date(2024, 2, 2),
        "date_to": date(2024, 2, 2),
    }
    result = queries.get_merged_history_qs(1, filters=filters)

    assert len(result) == 1
    entry = result[0]
    assert entry["id"] == 6
    assert entry["message"] == "edited"
    assert entry["entry_type"] == "log"
