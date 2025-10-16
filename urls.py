from django.urls import path
from .views import merged_history_view

app_name = "wagtail_unified_history"

urlpatterns = [
    path("pages/<int:page_id>/history/merged/", merged_history_view, name="merged_history"),
]
