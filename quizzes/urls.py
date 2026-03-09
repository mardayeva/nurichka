from django.urls import path
from .views import quiz_take, quiz_create_for_module, quiz_manage_for_module

urlpatterns = [
    path("<int:quiz_id>/take/", quiz_take, name="quiz_take"),
    path("module/<int:module_id>/create/", quiz_create_for_module, name="quiz_create_for_module"),
    path("module/<int:module_id>/manage/", quiz_manage_for_module, name="quiz_manage_for_module"),
]
