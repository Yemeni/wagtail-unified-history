from django.urls import path
from .views import merged_history_view

app_name = "wagtail_unified_history"

urlpatterns = [
    path("<int:page_id>/", merged_history_view, name="merged_history"),
]
