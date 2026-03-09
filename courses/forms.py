from django import forms
from .models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "subject", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"class":"form-control"}),
            "subject": forms.TextInput(attrs={"class":"form-control"}),
            "description": forms.Textarea(attrs={"class":"form-control", "rows":4}),
        }