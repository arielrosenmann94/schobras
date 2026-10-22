from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "panel"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("ingresar/", views.PanelLoginView.as_view(), name="login"),
    path("salir/", LogoutView.as_view(), name="logout"),
]
