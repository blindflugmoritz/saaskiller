"""
islands templatetag — loads Svelte island assets (JS + CSS) built by the
islands Vite build into backend/static/islands/.

Usage in Django templates:
    {% load islands %}
    {% island_assets %}   {# emits <link> + <script type="module"> tags #}

The tag reads from Django's staticfiles storage so whitenoise's
CompressedManifestStaticFilesStorage handles cache-busting automatically.
Both islands.js and islands.css are collected alongside Django admin static.
"""
# === FEATURE: cms ===
import logging

from django import template
from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.html import format_html, mark_safe

logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag
def island_assets():
    """Emit the <link> and <script type="module"> tags for the islands bundle.

    Falls back gracefully if the islands build hasn't been run yet (dev).
    In production, logs a warning when assets are missing so the failure is visible.
    """
    tags = []

    for asset, tag_fn in [
        ("islands/islands.css", lambda u: format_html('<link rel="stylesheet" href="{}">', u)),
        ("islands/islands.js", lambda u: format_html('<script type="module" src="{}"></script>', u)),
    ]:
        try:
            tags.append(tag_fn(staticfiles_storage.url(asset)))
        except Exception:
            if not settings.DEBUG:
                logger.warning(
                    "island_assets: %s not found in staticfiles. "
                    "Run `make build-islands` then `python manage.py collectstatic`.",
                    asset,
                )

    return mark_safe("\n    ".join(tags))
# === END FEATURE: cms ===
