from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import CustomUser

class OwnerCreationForm(forms.ModelForm):
    """
    A form for creating new owners in the admin without requiring a password.
    """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput, required=False)

    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'phone_number', 'shop_type', 'is_active', 'role')

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("The two password fields didn't match.")
        return cleaned_data

    def save(self, commit=True):
        owner = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            owner.set_password(password)
        else:
            owner.set_unusable_password()
        if commit:
            owner.save()
        return owner

class OwnerChangeForm(forms.ModelForm):
    """
    A form for updating owners in the admin interface.
    """
    password = ReadOnlyPasswordHashField(label=("Password"), required=False)

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'name', 'phone_number', 'shop_type', 'role','is_active', 'is_staff')

    def clean_password(self):
        return self.initial["password"]
