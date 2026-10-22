from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q

from projects.models import Category, Project


class PanelAuthenticationForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Usuario o contraseña incorrectos.",
    }


class OptionalOrderMixin:
    """El orden es opcional para la editora: vacío significa 0."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order"].required = False

    def clean_order(self):
        return self.cleaned_data.get("order") or 0


class CategoryForm(OptionalOrderMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "order", "is_active"]
        labels = {
            "name": "Nombre",
            "order": "Orden (número menor aparece primero)",
            "is_active": "Activa (aparece al crear proyectos)",
        }


class ProjectForm(OptionalOrderMixin, forms.ModelForm):
    construction_systems = forms.MultipleChoiceField(
        label="Sistemas constructivos",
        choices=Project.ConstructionSystem.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Project
        fields = [
            "title",
            "category",
            "intervention_type",
            "commune",
            "region",
            "construction_systems",
            "area_m2",
            "year",
            "description",
            "is_featured",
            "order",
        ]
        labels = {
            "title": "Nombre del proyecto",
            "category": "Categoría",
            "intervention_type": "Tipo de intervención",
            "commune": "Comuna",
            "region": "Región",
            "area_m2": "Superficie (m²)",
            "year": "Año",
            "description": "Descripción",
            "is_featured": "Destacado en la portada",
            "order": "Orden (número menor aparece primero)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        active = Q(is_active=True)
        if self.instance.category_id:
            active |= Q(pk=self.instance.category_id)
        self.fields["category"].queryset = Category.objects.filter(active)
        self.fields["category"].empty_label = "Elige una categoría"
