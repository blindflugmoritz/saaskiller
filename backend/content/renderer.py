from django.utils.html import format_html, mark_safe
from content_editor.contents import contents_for_item
from content.models import PageRichText, PageImage, PageHTML

PLUGINS = [PageRichText, PageImage, PageHTML]


def _render_plugin(plugin):
    if isinstance(plugin, PageRichText):
        return {"type": "richtext", "html": plugin.text}
    if isinstance(plugin, PageImage):
        return {
            "type": "image",
            "url": plugin.image.url if plugin.image else None,
            "caption": plugin.caption,
            "alt": "",
        }
    if isinstance(plugin, PageHTML):
        return {"type": "html", "html": plugin.html}
    return None


def regions_for_page(page):
    # === FEATURE: cms ===
    contents = contents_for_item(page, plugins=PLUGINS)
    result = {}
    for region in page.regions:
        blocks = [_render_plugin(p) for p in contents[region.key]]
        result[region.key] = [b for b in blocks if b is not None]
    return result
    # === END FEATURE: cms ===


def _render_plugin_html(plugin):
    # === FEATURE: cms ===
    """Render a single plugin to a SafeString for use in Django templates."""
    if isinstance(plugin, PageRichText):
        return mark_safe(plugin.text) if plugin.text else None
    if isinstance(plugin, PageHTML):
        return mark_safe(plugin.html) if plugin.html else None
    if isinstance(plugin, PageImage):
        url = plugin.image.url if plugin.image else None
        if not url:
            return None
        return format_html(
            '<figure class="mb-6">'
            '<img src="{}" alt="{}" class="w-full rounded-lg" />'
            '{}'
            '</figure>',
            url,
            plugin.caption or "",
            format_html(
                '<figcaption class="text-sm text-center mt-2 text-gray-500">{}</figcaption>',
                plugin.caption,
            ) if plugin.caption else mark_safe(""),
        )
    return None
    # === END FEATURE: cms ===


def render_regions_html(page):
    # === FEATURE: cms ===
    """Return {region_key: [SafeString, …]} for use in Django templates.

    Each item is either a SafeString of rendered HTML or an island marker
    (see IslandPlugin — not yet in models, added when interactive islands are needed).
    """
    contents = contents_for_item(page, plugins=PLUGINS)
    result = {}
    for region in page.regions:
        blocks = [_render_plugin_html(p) for p in contents[region.key]]
        result[region.key] = [b for b in blocks if b is not None]
    return result
    # === END FEATURE: cms ===
