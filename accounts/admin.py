from django.contrib import admin
from .models import Center, Profile


@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "phone", "created_at")
    search_fields = ("name", "owner__username", "owner__email")

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "center", "specialization", "center_name", "experience_years")
    search_fields = ("user__username", "user__email", "full_name", "specialization", "center_name", "center__name")
