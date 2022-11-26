from django.contrib import admin
from django.urls import path
from Labs.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", MainPage),
    path("login",LoginUser.as_view()),
    path("exercises/", Exercises),
]
