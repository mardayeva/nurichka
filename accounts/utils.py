from django.contrib.auth.decorators import user_passes_test

def teacher_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and hasattr(u, "profile") and u.profile.role == "TEACHER")(view_func)

def student_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and hasattr(u, "profile") and u.profile.role == "STUDENT")(view_func)


def center_admin_required(view_func):
    return user_passes_test(
        lambda u: u.is_authenticated and hasattr(u, "profile") and u.profile.role == "CENTER_ADMIN"
    )(view_func)
