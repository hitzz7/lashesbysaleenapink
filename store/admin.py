from datetime import datetime, date, time, timedelta
from django.contrib import admin
from django.core.mail import send_mail
from django.shortcuts import render
from django.urls import path
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

    def save_model(self, request, obj, form, change):
        """
        Send customer confirmation email only when booking becomes confirmed.
        """
        was_confirmed = False
        if change and obj.pk:
            previous = Booking.objects.filter(pk=obj.pk).only("is_confirmed").first()
            was_confirmed = bool(previous and previous.is_confirmed)

        super().save_model(request, obj, form, change)

        if obj.is_confirmed and not was_confirmed and obj.email:
            services_selected = ", ".join([str(s) for s in obj.services.all()])
            subject = "Your Booking Is Confirmed"
            message = (
                f"Hi {obj.name},\n\n"
                "Your booking has been confirmed.\n\n"
                f"Services: {services_selected}\n"
                f"Date: {obj.date}\n"
                f"Time: {obj.time}\n\n"
                "Thank you,\n"
                "Beautiful Eyelashes by Saleena"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[obj.email],
                fail_silently=True,
            )

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
        interval_min = int(request.GET.get("interval", 60))

        # Default: earliest upcoming booking date (confirmed or not),
        # otherwise today's date.
        today = date.today()
        first_upcoming_booking_date = (
            Booking.objects.filter(date__gte=today)
            .order_by("date")
            .values_list("date", flat=True)
            .first()
        )
        default_start = first_upcoming_booking_date or today
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

        # Build 7 days so weekend bookings are also visible.
        num_days = 7
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

        # Fetch all bookings for the week (confirmed + unconfirmed)
        end_date = days[-1]
        bookings = list(
            Booking.objects.filter(
                date__gte=days[0], 
                date__lte=end_date
            ).order_by("date", "time")
        )
        # Build grid: place bookings in the matching interval bucket.
        # This keeps bookings visible even if interval changes (e.g. 30 min).
        grid = []
        for si, slot_time in enumerate(slots):
            row = []
            slot_start_minutes = slot_time.hour * 60 + slot_time.minute
            next_slot_minutes = slot_start_minutes + interval_min
            for di, d in enumerate(days):
                cell_bookings = []
                for b in bookings:
                    if b.date != d:
                        continue
                    b_minutes = b.time.hour * 60 + b.time.minute
                    is_last_slot = si == len(slots) - 1
                    in_bucket = (
                        b_minutes >= slot_start_minutes
                        and (is_last_slot or b_minutes < next_slot_minutes)
                    )
                    if in_bucket:
                        cell_bookings.append(b)
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