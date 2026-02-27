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

    def clean(self):
        """
        Prevent multiple bookings at the same date and time.
        """
        cleaned_data = super().clean()
        booking_date = cleaned_data.get("date")
        booking_time = cleaned_data.get("time")

        if booking_date and booking_time:
            qs = Booking.objects.filter(date=booking_date, time=booking_time)
            # If this form is ever used for editing existing bookings, avoid
            # flagging the current instance as a conflict.
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise forms.ValidationError(
                    "This date and time has already been booked. "
                    "Please choose a different time."
                )

        return cleaned_data

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