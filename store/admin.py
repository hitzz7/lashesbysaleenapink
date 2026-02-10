from django.contrib import admin
from .models import ServiceCategory, Service, ServiceImage
from .models import Gallery,Booking


class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    inlines = [ServiceImageInline]


admin.site.register(ServiceCategory)

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at")
    list_filter = ("is_active",)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("name", "get_services", "date", "time", "is_confirmed", "created_at")
    list_filter = ("date", "services", "is_confirmed")
    search_fields = ("name", "email", "phone")

    def get_services(self, obj):
        return ", ".join([s.name for s in obj.services.all()])
    get_services.short_description = "Services"