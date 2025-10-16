from django.db.models import F, Value, CharField
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from wagtail.models import Page, PageLogEntry, Revision
from wagtail.log_actions import registry


def get_merged_history_qs(root_page, filters=None):
    """
    Return a unified list of PageLogEntry + Revision entries for a page
    and its descendants.  Uses Wagtail 7.1's built-in formatter per entry.
    """
    if isinstance(root_page, int):
        root_page = Page.objects.get(pk=root_page)

    descendant_ids = list(
        Page.objects.filter(path__startswith=root_page.path)
        .values_list("id", flat=True)
    )

    # make sure all log actions are scanned once
    if not registry.has_scanned_for_actions:
        registry.scan_for_actions()

    # -------------------------------------------------------
    # LOG ENTRIES
    # -------------------------------------------------------
    log_entries = (
        PageLogEntry.objects.filter(page_id__in=descendant_ids)
        .select_related("user", "page")
        .order_by("-timestamp")
    )

    log_data = []
    for entry in log_entries:
        try:
            # ✅ built-in Wagtail 7.1 formatter on each entry
            message = entry.formatter.format_message(entry) if entry.formatter else (
                entry.message or entry.action
            )
        except Exception:
            message = entry.message or entry.action

        log_data.append({
            "id": entry.id,
            "timestamp": entry.timestamp,
            "user_id": entry.user_id,
            "user__username": getattr(entry.user, "username", None),
            "page_id": entry.page_id,
            "page__title": getattr(entry.page, "title", "(deleted)"),
            "action": entry.action,
            "message": mark_safe(message),
            "entry_type": "log",
        })

    # -------------------------------------------------------
    # REVISIONS
    # -------------------------------------------------------
    page_ct_ids = [
        ContentType.objects.get_for_model(model).id
        for model in Page.__subclasses__()
        if not model._meta.abstract
    ]

    rev_qs = (
        Revision.objects.filter(content_type_id__in=page_ct_ids)
        .filter(object_id__in=descendant_ids)
        .select_related("user")
        .annotate(
            timestamp=F("created_at"),
            page_id=F("object_id"),
            action=Value("wagtail.revision.save", output_field=CharField()),
            message=Value("Revision saved", output_field=CharField()),
            entry_type=Value("revision", output_field=CharField()),
        )
        .values(
            "id",
            "timestamp",
            "user_id",
            "user__username",
            "page_id",
            "action",
            "message",
            "entry_type",
        )
    )

    page_titles = dict(Page.objects.filter(id__in=descendant_ids)
                       .values_list("id", "title"))

    rev_data = []
    for e in rev_qs:
        e["page__title"] = page_titles.get(e["page_id"], "(deleted)")
        rev_data.append(e)

    # -------------------------------------------------------
    # MERGE + FILTER + SORT
    # -------------------------------------------------------
    combined = log_data + rev_data

    if filters:
        if filters.get("user_id"):
            combined = [e for e in combined if e.get("user_id") == filters["user_id"]]
        if filters.get("date_from"):
            combined = [e for e in combined if e["timestamp"].date() >= filters["date_from"]]
        if filters.get("date_to"):
            combined = [e for e in combined if e["timestamp"].date() <= filters["date_to"]]

    combined.sort(key=lambda x: x["timestamp"], reverse=True)
    return combined
