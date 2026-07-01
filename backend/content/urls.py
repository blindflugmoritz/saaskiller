from django.urls import path
from content import views

urlpatterns = [
    # === FEATURE: cms ===
    path("page/", views.page_by_path, name="cms-page-by-path"),
    path("pages/", views.page_list, name="cms-page-list"),
    # === END FEATURE: cms ===
]
