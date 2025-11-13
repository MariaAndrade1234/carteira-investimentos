from django.urls import path

from core.debug_views import test_atomic_view


urlpatterns = [
    path("api/test_atomic/", test_atomic_view),
]
