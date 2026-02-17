from django.db import models


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    category = models.ForeignKey(
        ServiceCategory,
        related_name="services",
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    refillprice = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ServiceImage(models.Model):
    service = models.ForeignKey(
        Service,
        related_name="images",
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="services/")
    alt_text = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"Image for {self.service.name}"

from django.db import models


class Gallery(models.Model):
    title = models.CharField(max_length=150, blank=True)
    image = models.ImageField(upload_to="gallery/")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title if self.title else "Gallery Image"


class Booking(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    services = models.ManyToManyField('Service')
    date = models.DateField()
    time = models.TimeField()

    # ✅ Consent & health questions
    can_lie_still = models.BooleanField(default=False)
    wears_contacts = models.BooleanField(default=False)
    has_sensitivities = models.BooleanField(default=False)
    allergic_to_products = models.BooleanField(default=False)
    understands_risks = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=True)

    def __str__(self):
        service_names = ", ".join([s.name for s in self.services.all()])
        return f"{self.name} - {service_names} on {self.date} at {self.time}"