from django import forms

from .models import AdoptionRequest


class AdoptionRequestForm(forms.ModelForm):
    previous_pet_experience = forms.TypedChoiceField(
        label="Have you owned a pet before?",
        choices=[("True", "Yes"), ("False", "No")],
        coerce=lambda v: v == "True",
        widget=forms.RadioSelect,
    )

    class Meta:
        model = AdoptionRequest
        fields = ["address", "phone", "reason", "previous_pet_experience", "message"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2}),
            "reason": forms.Textarea(attrs={"rows": 3}),
            "message": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, user, pet, **kwargs):
        super().__init__(*args, **kwargs)
        # Set before validation so model.clean() can enforce the business rules.
        self.instance.user = user
        self.instance.pet = pet
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs["class"] = "form-control"
        self.fields["phone"].widget.attrs["placeholder"] = "+8801XXXXXXXXX"
