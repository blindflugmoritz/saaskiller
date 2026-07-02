import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from saaskiller.views import health, spa, FRONTEND_BUILD
# === FEATURE: cms ===
from content.views import cms_page_html
# === END FEATURE: cms ===

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
    # Static assets from the SvelteKit frontend build
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": os.path.join(FRONTEND_BUILD, "..", "build")}),
    # === FEATURE: cms ===
    # CMS HTML catch-all: must come BEFORE the SPA fallback so known CMS paths get
    # server-rendered HTML (crawlable, instant-live). Unknown paths fall through to
    # the SPA inside the view itself (cms_page_html calls spa() when no Page found).
    re_path(r"^(?P<path>.*)$", cms_page_html),
    # === END FEATURE: cms ===
    # SPA fallback — serves SvelteKit index.html for /dashboard, /auth/*, etc.
    re_path(r"^.*$", spa),
]
