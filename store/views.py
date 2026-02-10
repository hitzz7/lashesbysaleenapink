from django.shortcuts import render, get_object_or_404
from .forms import BookingForm
from .models import ServiceCategory, Service
from .models import Gallery
from django.shortcuts import render, redirect

def home(request):
    return render(request, 'Warzone/home.html')

def category_with_services(request):
    categories = ServiceCategory.objects.prefetch_related("services__images")

    return render(request, "Warzone/category_services.html", {
        "categories": categories
    })

def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk, is_active=True)

    return render(request, "Warzone/service_detail.html", {
        "service": service
    })

def gallery_view(request):
    images = Gallery.objects.filter(is_active=True).order_by("-created_at")

    return render(request, "Warzone/gallary.html", {
        "images": images
    })

from django.core.mail import send_mail
def booking_view(request, service_id=None):
    service = None
    if service_id:
        service = Service.objects.get(id=service_id)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            
            # Email
            services_selected = ", ".join([str(s) for s in booking.services.all()])
            subject = "New Booking Received"
            message = (
                f"A new booking has been made:\n\n"
                f"Name: {booking.name}\n"
                f"Email: {booking.email}\n"
                f"Phone: {booking.phone}\n"
                f"Services: {services_selected}\n"
                f"Date: {booking.date}\n"
                f"Time: {booking.time}\n"
            )
            recipient_list = ["najus77@gmail.com"]
            if booking.email and booking.email not in recipient_list:
                recipient_list.append(booking.email)
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=recipient_list,
                fail_silently=True,
            )
            return render(request, "Warzone/booking_success.html")
    else:
        # If service_id is sent, pre-fill form
        initial_data = {}
        if service:
            initial_data['services'] = [service]  # assuming your BookingForm has a services field
        form = BookingForm(initial=initial_data)

    return render(request, "Warzone/booking.html", {"form": form, "service": service})

def about(request):
    """
    Renders the About Us page.
    """
    return render(request, "Warzone/about.html")

def care(request):
    """
    Renders the About Us page.
    """
    return render(request, "Warzone/care.html")