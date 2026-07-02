# === FEATURE: cms ===
"""Cache invalidation for server-rendered CMS pages.

When a Page or any of its plugin models (PageRichText, PageImage, PageHTML) is
saved or deleted via the feincms3 admin, the rendered HTML cached by @cache_page
in cms_page_html must be cleared so editors see their changes immediately.

Simplest robust strategy: clear the entire cache on any CMS change.
At typical CMS scale (marketing pages, blog posts) this is perfectly acceptable —
cache rebuilds on next request in milliseconds.

For multi-worker setups (gunicorn --workers N): Django's default LocMemCache is
per-process, so cache invalidation in one worker doesn't reach the others. To get
true instant-live across all workers, configure a shared cache backend in settings.py:
  - DatabaseCache: create with `python manage.py createcachetable`, zero extra deps.
  - Redis/Memcached: if already in the stack (e.g. tasks feature uses Redis).
Until then the 15-minute TTL in @cache_page acts as a safety net.
"""
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from content.models import Page, PageHTML, PageImage, PageRichText


def _clear_cms_cache(**kwargs):
    """Clear all cached CMS-page HTML. Called on any Page or plugin change."""
    cache.clear()


# ── Page saves/deletes ────────────────────────────────────────────────────────

@receiver(post_save, sender=Page)
def on_page_save(sender, **kwargs):
    _clear_cms_cache()


@receiver(post_delete, sender=Page)
def on_page_delete(sender, **kwargs):
    _clear_cms_cache()


# ── Plugin saves/deletes (content edits don't touch the Page row) ─────────────

@receiver(post_save, sender=PageRichText)
def on_richtext_save(sender, **kwargs):
    _clear_cms_cache()


@receiver(post_delete, sender=PageRichText)
def on_richtext_delete(sender, **kwargs):
    _clear_cms_cache()


@receiver(post_save, sender=PageImage)
def on_image_save(sender, **kwargs):
    _clear_cms_cache()


@receiver(post_delete, sender=PageImage)
def on_image_delete(sender, **kwargs):
    _clear_cms_cache()


@receiver(post_save, sender=PageHTML)
def on_html_save(sender, **kwargs):
    _clear_cms_cache()


@receiver(post_delete, sender=PageHTML)
def on_html_delete(sender, **kwargs):
    _clear_cms_cache()
# === END FEATURE: cms ===
