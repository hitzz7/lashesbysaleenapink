from django import forms
from .models import Booking, ServiceCategory, Service

YES_NO_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)

class BookingForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Services",
    )

    agree_terms = forms.BooleanField(
        required=True,
        label="I agree to the terms and conditions",
        error_messages={
            "required": "You must agree to the terms and conditions to book."
        },
    )

    # ✅ Consent & health questions
    can_lie_still = forms.ChoiceField(
        choices=YES_NO_CHOICES,
        widget=forms.RadioSelect,
        label="Are you able to keep your eyes closed / lie still for up to 3 hours?",
        required=True,
    )

    wears_contacts = forms.ChoiceField(
        choices=YES_NO_CHOICES,
        widget=forms.RadioSelect,
        label="Do you wear contact lenses? (We recommend removing them)",
        required=True,
    )

    has_sensitivities = forms.ChoiceField(
        choices=YES_NO_CHOICES,
        widget=forms.RadioSelect,
        label="Do you have sensitivities such as itchy eyes or hay fever?",
        required=True,
    )

    allergic_to_products = forms.ChoiceField(
        choices=YES_NO_CHOICES,
        widget=forms.RadioSelect,
        label="Are you allergic to latex, acrylates, glue, tape or adhesives?",
        required=True,
    )

    understands_risks = forms.ChoiceField(
        choices=YES_NO_CHOICES,
        widget=forms.RadioSelect,
        label="I understand there are risks associated with eyelash extensions",
        required=True,
    )

    class Meta:
        model = Booking
        fields = [
            "name",
            "email",
            "phone",
            "services",
            "date",
            "time",
            "can_lie_still",
            "wears_contacts",
            "has_sensitivities",
            "allergic_to_products",
            "understands_risks",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
        }

    def clean_understands_risks(self):
        value = self.cleaned_data.get("understands_risks")
        if value is False:
            raise forms.ValidationError(
                "You must acknowledge the risks to proceed with the booking."
            )
        return value

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