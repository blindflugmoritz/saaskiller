from django.contrib import admin
from feincms3.admin import TreeAdmin
from content_editor.admin import ContentEditor, ContentEditorInline
from content.models import Page, PageRichText, PageImage, PageHTML


class RichTextInline(ContentEditorInline):
    model = PageRichText
    regions = ["main"]


class ImageInline(ContentEditorInline):
    model = PageImage
    regions = ["main"]


class HTMLInline(ContentEditorInline):
    model = PageHTML
    regions = ["main"]


@admin.register(Page)
class PageAdmin(ContentEditor, TreeAdmin):
    # === FEATURE: cms ===
    list_display = ["indented_title", "slug", "is_active", "static_path", "position"]
    list_editable = ["is_active"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [RichTextInline, ImageInline, HTMLInline]
    fieldsets = [
        (None, {"fields": ("title", "slug", "is_active")}),
        ("SEO", {"fields": ("meta_description",), "classes": ("collapse",)}),
        ("Advanced", {"fields": ("parent", "position", "static_path", "path"), "classes": ("collapse",)}),
    ]
    # === END FEATURE: cms ===
