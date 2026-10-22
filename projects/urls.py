from django.urls import path

from . import views

app_name = "projects"

# La ruta de categoría va antes que el detalle para que "categoria" no se lea como slug.
urlpatterns = [
    path("", views.project_list, name="list"),
    path("categoria/<slug:slug>/", views.project_category, name="category"),
    path("<slug:slug>/", views.project_detail, name="detail"),
]
