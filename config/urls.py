from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("pages.urls")),
    path("accounts/", include("accounts.urls")),

    path("teacher/", include("courses.urls_teacher")),
    path("student/", include("courses.urls_student")),
    path("center/", include("courses.urls_center")),

    path("learning/", include("learning.urls")),
    path("quizzes/", include("quizzes.urls")),
    path("certificates/", include("certificates.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
