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
