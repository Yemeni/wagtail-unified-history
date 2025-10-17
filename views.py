from datetime import datetime
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from wagtail.models import Page, PageLogEntry
from wagtail.admin.views.generic.history import HistoryFilterSet
from .queries import get_merged_history_qs


def merged_history_view(request, page_id):
    root_page = get_object_or_404(Page, id=page_id)

    descendant_ids = list(
        Page.objects.filter(path__startswith=root_page.path).values_list("id", flat=True)
    )
    base_qs = PageLogEntry.objects.filter(page_id__in=descendant_ids)
    filterset = HistoryFilterSet(request.GET or None, queryset=base_qs)

    filters = {}
    if filterset.is_valid():
        data = filterset.form.cleaned_data
        users = data.get("user") or []
        actions = data.get("action") or []
        filters = {
            "user_ids": [u.id for u in users],
            "actions": actions,
        }

    date_from_str = request.GET.get("timestamp_from")
    date_to_str = request.GET.get("timestamp_to")

    date_from = (
        datetime.strptime(date_from_str, "%Y-%m-%d").date() if date_from_str else None
    )
    date_to = datetime.strptime(date_to_str, "%Y-%m-%d").date() if date_to_str else None

    filters["date_from"] = date_from
    filters["date_to"] = date_to

    entries = get_merged_history_qs(root_page, filters)

    if filters.get("user_ids"):
        entries = [e for e in entries if e.get("user_id") in filters["user_ids"]]

    if filters.get("actions"):
        entries = [e for e in entries if e.get("action") in filters["actions"]]

    if date_from:
        entries = [e for e in entries if e["timestamp"].date() >= date_from]

    if date_to:
        entries = [e for e in entries if e["timestamp"].date() <= date_to]

    paginator = Paginator(entries, 50)
    page_num = request.GET.get("p", 1)
    entries = paginator.get_page(page_num)

    template_name = "wagtail_unified_history/merged_history.html"
    hx_request_header = request.headers.get("HX-Request")
    hx_target_header = request.headers.get("HX-Target", "")
    wagtail_swap_target = request.headers.get("Wagtail-Swap-Target", "")
    accept_header = request.headers.get("Accept", "")

    wants_partial = False
    if hx_request_header:
        wants_partial = True
        if hx_target_header:
            wants_partial = hx_target_header.lstrip("#").strip() == "listing-results"
    elif wagtail_swap_target:
        wants_partial = wagtail_swap_target.lstrip("#").strip() == "listing-results"
    elif "text/vnd.wagtailadmin.partial+html" in accept_header:
        wants_partial = True

    if wants_partial:
        template_name = "wagtail_unified_history/includes/merged_history_results.html"

    return render(
        request,
        template_name,
        {
            "root_page": root_page,
            "entries": entries,
            "filters": filterset,
        },
    )
