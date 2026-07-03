from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from content.models import Page
from content.renderer import regions_for_page, render_regions_html


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def page_by_path(request):
    # === FEATURE: cms ===
    path = request.query_params.get("path", "/")
    if not path.startswith("/"):
        path = f"/{path}"
    # feincms3 stores paths with trailing slash — normalize so /home and /home/ both resolve
    if not path.endswith("/"):
        path = f"{path}/"

    page = Page.objects.filter(path=path, is_active=True).first()
    if page is None:
        return JsonResponse({"detail": "Not found."}, status=404)

    regions = regions_for_page(page)

    return JsonResponse({
        "id": page.pk,
        "title": page.title,
        "slug": page.slug,
        "path": page.path,
        "meta_description": page.meta_description,
        "regions": regions,
    })
    # === END FEATURE: cms ===


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def page_list(request):
    # === FEATURE: cms ===
    pages = Page.objects.filter(is_active=True).values("id", "title", "slug", "path", "meta_description")
    return JsonResponse({"pages": list(pages)})
    # === END FEATURE: cms ===


# === FEATURE: cms ===
# Prefixes that belong to Django/API — never attempt a CMS page lookup for these.
_NON_CMS_PREFIXES = ("api/", "admin/", "static/", "media/", "accounts/")


@cache_page(60 * 15)  # 15-minute TTL — post_save signal in signals.py clears on edits
def cms_page_html(request, path=""):
    """Server-render a feincms3 CMS page as full HTML.

    Registered in saaskiller/urls.py as a catch-all BEFORE the SPA fallback so
    known CMS paths get real HTML (crawlable), unknown paths fall through to the SPA.

    The @cache_page decorator caches the rendered HTML in Django's cache backend.
    Cache is invalidated by post_save/post_delete signals on Page and plugin models
    (see content/signals.py) so editors see changes immediately after saving.

    SECURITY NOTE: PageRichText and PageHTML content is rendered as raw HTML via
    mark_safe(). This is intentional — these fields are only editable by trusted
    Django superusers/staff via the admin. Never expose them to untrusted input.
    """
    from saaskiller.views import spa

    # Pass through paths that belong to Django internals / API — avoids turning
    # broken /api/typo/ requests into 200 OK HTML responses seen by API clients.
    stripped = path.lstrip("/")
    if any(stripped.startswith(p) for p in _NON_CMS_PREFIXES):
        return spa(request, path)

    # Normalise to feincms3 convention: /home/ (leading + trailing slash)
    if not path.startswith("/"):
        path = f"/{path}"
    if not path.endswith("/"):
        path = f"{path}/"

    page = Page.objects.filter(path=path, is_active=True).first()
    if page is None:
        # No CMS page for this path — pass through to the SvelteKit SPA fallback
        return spa(request, path)

    regions = render_regions_html(page)
    return render(request, "content/page.html", {"page": page, "regions": regions})
# === END FEATURE: cms ===
