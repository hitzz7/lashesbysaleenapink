from django import forms
from .models import Booking, ServiceCategory, Service

class BookingForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Services"
    )

    class Meta:
        model = Booking
        fields = ["name", "email", "phone", "services", "date", "time"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        grouped_choices = []

        categories = ServiceCategory.objects.prefetch_related("services")

        for category in categories:
            services = category.services.filter(is_active=True)
            if services.exists():
                grouped_choices.append(
                    (category.name, [(service.id, service.name) for service in services])
                )

        self.fields["services"].choices = grouped_choices