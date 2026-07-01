import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

FRONTEND_BUILD = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "frontend", "build"
)


def health(request):
    return JsonResponse({"status": "ok"})


def spa(request, path=""):
    index = os.path.join(FRONTEND_BUILD, "index.html")
    if os.path.exists(index):
        return serve(request, "index.html", document_root=FRONTEND_BUILD)
    return JsonResponse({"error": "Frontend not built. Run: cd frontend && npm run build"}, status=404)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health, name="health"),
    path("api/auth/", include("users.urls")),
    path("api/auth/social/", include("dj_rest_auth.registration.urls")),
    path("accounts/", include("allauth.urls")),  # OAuth2 callbacks
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # === FEATURE: workspaces ===
    path("api/workspaces/", include("workspaces.urls")),
    # === END FEATURE: workspaces ===
    # === FEATURE: apikeys ===
    path("api/keys/", include("apikeys.urls")),
    # === END FEATURE: apikeys ===
    # === FEATURE: stripe ===
    path("api/billing/", include("billing.urls")),
    # === END FEATURE: stripe ===
    # === FEATURE: cms ===
    path("api/cms/", include("content.urls")),
    # === END FEATURE: cms ===
    # Static + SPA fallback
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": os.path.join(FRONTEND_BUILD, "..", "build")}),
    re_path(r"^.*$", spa),
]
