from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.views.generic.base import RedirectView
from django.urls import path
from django.urls import reverse_lazy
from Labs.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", MainPage, name="mainpage"),
    path("login", LoginUser.as_view(next_page="mainpage")),
    path("exercises/", Exercises, name="tasks"),
    path("logout/", LogoutView.as_view(next_page="mainpage"), name="logout"),
    path(
        "accounts/profile/",
        RedirectView.as_view(url=reverse_lazy("mainpage"), permanent=True),
    ),
    path("reset_progress", clear_solved_tasks),
    path('register', RegisterUser.as_view(), name='register')
]
