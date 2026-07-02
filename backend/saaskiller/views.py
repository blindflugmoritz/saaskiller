"""Core Django views for the SaasKiller backend.

Keeping these in a separate module (not urls.py) allows other views — e.g. the
CMS HTML view — to import and call spa() without creating circular imports.
"""
import os
from django.http import JsonResponse
from django.views.static import serve

FRONTEND_BUILD = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "..", "frontend", "build"
)


def health(request):
    return JsonResponse({"status": "ok"})


def spa(request, path=""):
    """Serve the SvelteKit SPA shell (frontend/build/index.html).

    Used as the final fallback for all routes not handled by API or CMS views.
    Also called directly by cms_page_html when no matching CMS Page is found,
    so /dashboard, /auth/*, and any unknown path still get the SPA.
    """
    index = os.path.join(FRONTEND_BUILD, "index.html")
    if os.path.exists(index):
        return serve(request, "index.html", document_root=FRONTEND_BUILD)
    return JsonResponse(
        {"error": "Frontend not built. Run: cd frontend && npm run build"},
        status=404,
    )
