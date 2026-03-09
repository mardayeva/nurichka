from django.conf import settings


def site_meta(request):
    default = {
        "name": "Learning Center",
        "short_name": "LMS",
        "tagline": "Professional ta'lim platformasi",
        "phone": "",
        "email": "",
        "address": "",
        "hours": "",
    }
    data = default | getattr(settings, "SITE_META", {})
    return {"site_meta": data}
