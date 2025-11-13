from django.urls import path

import core.debug_views as _debug_views


urlpatterns = [
    path("api/test_atomic/", _debug_views.test_atomic_view),
]
