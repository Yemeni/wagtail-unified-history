from wagtail import hooks
from wagtail.admin.action_menu import ActionMenuItem
from django.urls import reverse


class MergedHistoryMenuItem(ActionMenuItem):
    name = "merged_history"
    label = "Merged History"
    icon_name = "history"

    def is_shown(self, context):
        """Wagtail 7.x passes only `context`; get request from it."""
        page = context.get("page")
        return bool(page)

    def get_url(self, context):
        page = context.get("page")
        if not page:
            return "#"
        return reverse("wagtail_unified_history:merged_history", args=[page.id])


@hooks.register("register_page_action_menu_item")
def register_merged_history_item():
    return MergedHistoryMenuItem(order=90)
