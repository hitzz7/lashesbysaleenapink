from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Service


class ServiceSitemap(Sitemap):
    """Sitemap for Service detail pages."""

    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Service.objects.filter(is_active=True)

    def location(self, obj):
        return reverse("store:service_detail", args=[obj.pk])

    def lastmod(self, obj):
        return obj.created_at


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages."""

    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return ["store:home", "store:category_services", "store:gallery", "store:booking", "store:about", "store:care", "store:contact"]

    def location(self, item):
        return reverse(item)