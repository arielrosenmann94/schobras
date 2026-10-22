from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "panel"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("ingresar/", views.PanelLoginView.as_view(), name="login"),
    path("salir/", LogoutView.as_view(), name="logout"),
    path("proyectos/nuevo/", views.ProjectCreateView.as_view(), name="project_create"),
    path("proyectos/<uuid:pk>/", views.ProjectUpdateView.as_view(), name="project_edit"),
    path("proyectos/<uuid:pk>/eliminar/", views.ProjectDeleteView.as_view(), name="project_delete"),
    path(
        "proyectos/<uuid:pk>/publicar/",
        views.ProjectTogglePublishView.as_view(),
        name="project_toggle_publish",
    ),
    path("proyectos/<uuid:pk>/fotos/", views.ProjectPhotosView.as_view(), name="project_photos"),
    path("fotos/<uuid:pk>/subir/", views.PhotoUpView.as_view(), name="photo_up"),
    path("fotos/<uuid:pk>/bajar/", views.PhotoDownView.as_view(), name="photo_down"),
    path("fotos/<uuid:pk>/portada/", views.PhotoCoverView.as_view(), name="photo_cover"),
    path("fotos/<uuid:pk>/eliminar/", views.PhotoDeleteView.as_view(), name="photo_delete"),
    path("configuracion/", views.SiteSettingsView.as_view(), name="settings"),
    path("categorias/", views.CategoryListView.as_view(), name="categories"),
    path("categorias/nueva/", views.CategoryCreateView.as_view(), name="category_create"),
    path("categorias/<uuid:pk>/", views.CategoryUpdateView.as_view(), name="category_edit"),
    path("categorias/<uuid:pk>/eliminar/", views.CategoryDeleteView.as_view(), name="category_delete"),
]
