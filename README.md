# 🕓 Wagtail Unified History

**Wagtail Unified History** is a custom Wagtail admin extension that provides a **merged activity log** for each page.  
It unifies Wagtail’s `PageLogEntry`, workflow events, and comments into a single, filterable history view — displayed with the same modern Wagtail filter UI (Action / User / Date).

---

## 🚀 Features

- Displays a **merged history table** for any page (`PageLogEntry`, workflow logs, comments, etc.)
- Uses Wagtail’s native **filter dropdown (funnel icon)** for filtering by:
  - Action type (create, edit, publish, etc.)
  - User
  - Date range
- Fully integrated into the Wagtail Admin interface
- Works with **Wagtail 7.1+**
- Compatible with custom dashboards and other admin extensions

---

## 📁 Project Structure

```text
wagtail_unified_history/
│
├── **init**.py
├── views.py
├── queries.py
├── urls.py
├── templates/
│   └── wagtail_unified_history/
│       └── merged_history.html
└── README.md
```

---

## ⚙️ Installation

1. Add the app to your Django project:

   ```python
   INSTALLED_APPS = [
       # your existing apps …
       "wagtail_unified_history",
       # wagtail admin should be after
       "wagtail.admin",
   ]
    ```
2. Include the admin route in your main `urls.py`:

   ```python
   from django.urls import path, include

   urlpatterns = [
       path("admin/wagtail-unified-history/", include("wagtail_unified_history.urls")),
       # then your default admin urls after the wagtail unified history
       path("admin/", include(wagtailadmin_urls)),
       # other admin and site urls …
   ]
   ```
3. Restart your dev server:

   ```bash
   python manage.py runserver
   ```

---

## 🧭 Usage

* Open any Wagtail page edit view.
* In the top-right toolbar, click **History**.
* A new **“Merged History”** button (or link) will appear — click it to view the unified history table.

The view will display all available log entries (page actions, comments, workflow events, etc.), along with:

* User name
* Page link
* Action message
* Date/time

You can filter entries using the **Filter** dropdown:

* By action type (create, edit, publish…)
* By user
* By date range (with date picker)

---

## 🧩 Technical Notes

* The view uses `get_merged_history_qs()` (from `queries.py`) to combine different history sources.
* Filtering is powered by `HistoryFilterSet` from `wagtail.admin.views.generic.history`.
* The template `merged_history.html` extends Wagtail’s default admin base and reuses `_filters.html` for the native filter UI.

---

**Author:** Yousef Al-Hadhrami
**Frameworks:** Django 5.2.4 / Wagtail 7.1.1 / Python 3.12
**Last Updated:** October 2025

