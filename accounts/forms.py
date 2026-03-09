from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Profile

User = get_user_model()


class RegisterForm(UserCreationForm):
    ROLE_CHOICES = (
        ("TEACHER", "O'qituvchi"),
        ("STUDENT", "Student"),
        ("CENTER_ADMIN", "Markaz admini"),
    )

    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2", "role")

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["username"]
        user.first_name = self.cleaned_data["first_name"].strip()
        user.last_name = self.cleaned_data["last_name"].strip()
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Username yoki Email",
        widget=forms.TextInput(attrs={"class": "form-control", "autofocus": True}),
    )
    password = forms.CharField(
        label="Parol",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    def clean_username(self):
        return self.cleaned_data["username"].strip()

    def clean(self):
        username_input = self.cleaned_data.get("username")
        if username_input:
            if "@" in username_input:
                user = User.objects.filter(email__iexact=username_input).first()
                if user:
                    self.cleaned_data["username"] = user.get_username()
            else:
                user = User.objects.filter(username__iexact=username_input).first()
                if user:
                    self.cleaned_data["username"] = user.get_username()
        return super().clean()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            "avatar",
            "full_name",
            "phone",
            "center_name",
            "specialization",
            "experience_years",
            "linkedin_url",
            "bio",
        )
        widgets = {
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "To'liq ism"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+998 ..."}),
            "center_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "O'quv markaz nomi"}),
            "specialization": forms.TextInput(attrs={"class": "form-control", "placeholder": "Masalan: Matematika"}),
            "experience_years": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "linkedin_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://..."}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Qisqa ma'lumot"}),
        }
