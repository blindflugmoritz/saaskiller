from django.db import models
from django.utils.html import mark_safe
from feincms3.pages import AbstractPage
from feincms3.plugins.image import Image
from feincms3.plugins.html import HTML
from content_editor.models import Region, create_plugin_base


class Page(AbstractPage):
    # === FEATURE: cms ===
    regions = [
        Region(key="main", title="Main content"),
    ]

    meta_description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["position"]
        verbose_name = "page"
        verbose_name_plural = "pages"

    def __str__(self):
        return self.title


PagePlugin = create_plugin_base(Page)


class PageRichText(PagePlugin):
    # === FEATURE: cms ===
    # Plain TextField — no CKEditor dependency, no security warnings.
    # Accepts HTML; sanitize on save if needed.
    text = models.TextField(blank=True, verbose_name="text (HTML)")

    class Meta:
        ordering = ["ordering"]
        verbose_name = "rich text"

    def __str__(self):
        return self.text[:50] if self.text else "(empty)"

    def render(self):
        return mark_safe(self.text)


class PageImage(Image, PagePlugin):
    # === FEATURE: cms ===
    caption = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["ordering"]
        verbose_name = "image"


class PageHTML(HTML, PagePlugin):
    # === FEATURE: cms ===
    class Meta:
        ordering = ["ordering"]
        verbose_name = "HTML block"
    # === END FEATURE: cms ===
