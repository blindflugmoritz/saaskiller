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
from django import template
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.html import format_html, mark_safe

register = template.Library()


@register.simple_tag
def island_assets():
    """Emit the <link> and <script type="module"> tags for the islands bundle.

    Falls back gracefully if the islands build hasn't been run yet (dev).
    """
    tags = []

    # CSS
    try:
        css_url = staticfiles_storage.url("islands/islands.css")
        tags.append(format_html('<link rel="stylesheet" href="{}">', css_url))
    except Exception:
        # Islands CSS not collected yet — skip silently in dev
        pass

    # JS (type=module so it doesn't block render and supports ES2020+ syntax)
    try:
        js_url = staticfiles_storage.url("islands/islands.js")
        tags.append(format_html('<script type="module" src="{}"></script>', js_url))
    except Exception:
        # Islands JS not built yet — skip silently in dev
        pass

    return mark_safe("\n    ".join(tags))
# === END FEATURE: cms ===
