from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from wagtail.models import Page
from .queries import get_merged_history_qs
from .filters import HistoryFilterForm


def merged_history_view(request, page_id):
    root_page = get_object_or_404(Page, id=page_id)
    form = HistoryFilterForm(request.GET or None)

    # Base filters from the form
    filters = {}
    if form.is_valid():
        filters = {
            "user_id": form.cleaned_data.get("user").id if form.cleaned_data.get("user") else None,
            "date_from": form.cleaned_data.get("date_from"),
            "date_to": form.cleaned_data.get("date_to"),
        }

    # Extra filter from querystring (?entry_type=log)
    entry_type = request.GET.get("entry_type")

    # Always pass a Page instance, not its id
    qs = get_merged_history_qs(root_page, filters)

    # Optional type filter
    if entry_type:
        qs = [e for e in qs if e.get("entry_type") == entry_type]

    # Pagination
    paginator = Paginator(qs, 50)
    page_num = request.GET.get("p", 1)
    entries = paginator.get_page(page_num)

    return render(
        request,
        "wagtail_unified_history/merged_history.html",
        {
            "root_page": root_page,
            "entries": entries,
            "form": form,
            "entry_type": entry_type,
            "query_params": request.GET.urlencode(),
        },
    )
