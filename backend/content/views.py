from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from content.models import Page
from content.renderer import regions_for_page


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def page_by_path(request):
    # === FEATURE: cms ===
    path = request.query_params.get("path", "/")
    if not path.startswith("/"):
        path = f"/{path}"

    page = Page.objects.filter(path=path, is_active=True).first()
    if page is None:
        return JsonResponse({"detail": "Not found."}, status=404)

    regions = regions_for_page(page)

    return JsonResponse({
        "id": page.pk,
        "title": page.title,
        "slug": page.slug,
        "path": page.path,
        "metaDescription": page.meta_description,
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
