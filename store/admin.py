from datetime import datetime, date, time, timedelta
from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from django.utils.html import format_html
from .models import ServiceCategory, Service, ServiceImage
from .models import Gallery, Booking


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
    list_display = (
        "name",
        "get_services",
        "date",
        "time",
        "can_lie_still",
        "wears_contacts",
        "has_sensitivities",
        "allergic_to_products",
        "understands_risks",
        "is_confirmed",
        "created_at",
    )

    list_filter = (
        "date",
        "services",
        "is_confirmed",
        "can_lie_still",
        "wears_contacts",
        "has_sensitivities",
        "allergic_to_products",
        "understands_risks",
    )

    search_fields = ("name", "email", "phone")
    list_per_page = 25
    ordering = ("-created_at",)
    change_list_template = "admin/store/booking/change_list.html"

    def get_services(self, obj):
        return ", ".join(s.name for s in obj.services.all())

    get_services.short_description = "Services"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("schedule/", self.admin_site.admin_view(self.schedule_view), name="store_booking_schedule"),
        ]
        return custom + urls

    def schedule_view(self, request):
        """Weekly appointment schedule grid (start date, start time, interval)."""
        # Parse query params with defaults
        start_date_str = request.GET.get("start_date")
        start_time_str = request.GET.get("start_time", "9:00")
        interval_min = int(request.GET.get("interval", 15))

        # Default: 21 February (current year)
        today = date.today()
        default_start = date(today.year, 2, 21)
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                start_date = default_start
        else:
            start_date = default_start

        # Start time: 9:00 AM default
        if ":" in start_time_str:
            try:
                h, m = map(int, start_time_str.replace("AM", "").replace("PM", "").strip().split(":")[:2])
                start_dt = datetime.combine(start_date, time(h, m, 0))
            except (ValueError, IndexError):
                start_dt = datetime.combine(start_date, time(9, 0, 0))
        else:
            start_dt = datetime.combine(start_date, time(9, 0, 0))

        # Build 5 weekdays (Mon–Fri)
        num_days = 5
        days = [start_date + timedelta(days=i) for i in range(num_days)]

        # Build time slots (every interval from 9:00 AM to 9:00 PM)
        slots = []
        current_time = start_dt.time()
        end_time = time(21, 0)  # 9:00 PM
        while current_time <= end_time:
            slots.append(current_time)
            # Calculate next slot
            total_minutes = current_time.hour * 60 + current_time.minute + interval_min
            next_hour = total_minutes // 60
            next_minute = total_minutes % 60
            if next_hour >= 24:
                break
            current_time = time(next_hour, next_minute)

        # Fetch only confirmed bookings for the week
        end_date = days[-1]
        bookings = list(
            Booking.objects.filter(
                date__gte=days[0], 
                date__lte=end_date,
                is_confirmed=True
            ).order_by("date", "time")
        )
        # Build grid: grid[slot_index][day_index] = list of bookings for that cell (same date, same time slot)
        grid = []
        for si, slot_time in enumerate(slots):
            row = []
            for di, d in enumerate(days):
                cell_bookings = [b for b in bookings if b.date == d and b.time == slot_time]
                row.append(cell_bookings)
            grid.append((slot_time, row))

        context = {
            "title": "Appointment Schedule",
            "opts": self.model._meta,
            "start_date": start_date,
            "start_time_str": start_time_str,
            "interval": interval_min,
            "days": days,
            "slots": slots,
            "grid": grid,
        }
        return render(request, "admin/store/booking/schedule.html", context)