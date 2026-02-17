from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
app_name = 'store'

urlpatterns = [
    path('',views.home, name="home"),
    path("category/", views.category_with_services, name="category_services"),
    path("service/<int:pk>/", views.service_detail, name="service_detail"),
    path("gallery/", views.gallery_view, name="gallery"),
    path("booking/", views.booking_view, name="booking"),
    path("about/", views.about, name="about"),
    path("care/", views.care, name="care"),
    path("contact/", views.Contact, name="contact"),
        
]

