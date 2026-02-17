from django.shortcuts import render, get_object_or_404
from .forms import BookingForm
from .models import ServiceCategory, Service
from .models import Gallery
from django.shortcuts import render, redirect

def home(request):
    categories = ServiceCategory.objects.prefetch_related("services__images")
    services = Service.objects.filter(is_active=True)
    images = Gallery.objects.filter(is_active=True).order_by("-created_at")
    return render(request, 'Warzone/home.html', {
        "categories": categories,
        "services": services,
        "images": images,
    })

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
    service_id = service_id or request.GET.get("service")

    if service_id:
        try:
            service = Service.objects.get(id=service_id)
        except (Service.DoesNotExist, ValueError):
            pass

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()

            # Services text
            services_selected = ", ".join([str(s) for s in booking.services.all()])

            # Helper to convert True/False → Yes/No
            def yes_no(value):
                return "Yes" if value else "No"

            subject = "New Booking Received"
            message = (
                f"A new booking has been made:\n\n"
                f"Name: {booking.name}\n"
                f"Email: {booking.email}\n"
                f"Phone: {booking.phone}\n"
                f"Services: {services_selected}\n"
                f"Date: {booking.date}\n"
                f"Time: {booking.time}\n\n"

                f"Client Declarations:\n"
                f"Can lie still for 3 hours: {yes_no(booking.can_lie_still)}\n"
                f"Wears contact lenses: {yes_no(booking.wears_contacts)}\n"
                f"Has sensitivities / hay fever: {yes_no(booking.has_sensitivities)}\n"
                f"Allergic to products: {yes_no(booking.allergic_to_products)}\n"
                f"Understands risks: {yes_no(booking.understands_risks)}\n"
            )

            recipient_list = ["Saleename1994@gmail.com"]
            if booking.email and booking.email not in recipient_list:
                recipient_list.append(booking.email)

            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=recipient_list,
                fail_silently=True,
            )

            return render(request, "Warzone/booking_success.html", {
                "booking": booking,
            })
    else:
        initial_data = {}
        if service:
            initial_data["services"] = [service]

        form = BookingForm(initial=initial_data)

    return render(request, "Warzone/booking.html", {
        "form": form,
        "service": service
    })

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

def Contact(request):
    """
    Renders the About Us page.
    """
    return render(request, "Warzone/contact.html")
    