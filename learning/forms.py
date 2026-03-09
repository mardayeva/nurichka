from django import forms
from .models import Module, Assignment, AssignmentSubmission

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = [
            "title",
            "order",
            "video_url",
            "content",
            "resource_file",
            "resource_links",
            "passing_score",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class":"form-control"}),
            "order": forms.NumberInput(attrs={"class":"form-control"}),
            "video_url": forms.URLInput(attrs={"class":"form-control"}),
            "content": forms.Textarea(attrs={"class":"form-control","rows":5}),
            "resource_file": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.doc,.docx,.ppt,.pptx,.png,.jpg,.jpeg,.webp,.gif,.svg,image/*",
                }
            ),
            "resource_links": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Har qatorga bitta link yozing",
                }
            ),
            "passing_score": forms.NumberInput(attrs={"class":"form-control"}),
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "description", "due_date", "max_score"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "due_date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "max_score": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ["text_answer", "file"]
        widgets = {
            "text_answer": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
