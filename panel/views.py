from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from projects import services
from projects.models import Category, Project

from .forms import CategoryForm, PanelAuthenticationForm, ProjectForm
from .permissions import PanelAccessMixin


class PanelLoginView(LoginView):
    template_name = "panel/login.html"
    authentication_form = PanelAuthenticationForm
    redirect_authenticated_user = True


class HomeView(PanelAccessMixin, ListView):
    template_name = "panel/home.html"
    context_object_name = "projects"

    def get_queryset(self):
        return Project.objects.select_related("category").order_by("-updated_at")


class ProjectCreateView(PanelAccessMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "panel/project_form.html"

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Proyecto creado como borrador. Ahora sube las fotos.")
        return redirect("panel:project_photos", pk=self.object.pk)


class ProjectUpdateView(PanelAccessMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "panel/project_form.html"
    success_url = reverse_lazy("panel:home")

    def form_valid(self, form):
        messages.success(self.request, "Cambios guardados.")
        return super().form_valid(form)


class ProjectDeleteView(PanelAccessMixin, DeleteView):
    model = Project
    template_name = "panel/confirm_delete.html"
    success_url = reverse_lazy("panel:home")
    extra_context = {"kind": "proyecto", "cancel_url": reverse_lazy("panel:home")}

    def form_valid(self, form):
        messages.success(self.request, "Proyecto eliminado.")
        return super().form_valid(form)


class ProjectTogglePublishView(PanelAccessMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if project.status == Project.Status.PUBLISHED:
            services.unpublish(project)
            messages.success(request, "El proyecto ya no se ve en la web.")
        else:
            try:
                services.publish(project)
            except services.PublishError as error:
                messages.error(request, error.args[0])
            else:
                messages.success(request, "El proyecto ya está publicado en la web.")
        return redirect("panel:home")


class ProjectPhotosView(PanelAccessMixin, DetailView):
    model = Project
    template_name = "panel/photos.html"
    context_object_name = "project"


class CategoryListView(PanelAccessMixin, ListView):
    model = Category
    template_name = "panel/categories.html"
    context_object_name = "categories"


class CategoryCreateView(PanelAccessMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "panel/category_form.html"
    success_url = reverse_lazy("panel:categories")

    def form_valid(self, form):
        messages.success(self.request, "Categoría creada.")
        return super().form_valid(form)


class CategoryUpdateView(PanelAccessMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "panel/category_form.html"
    success_url = reverse_lazy("panel:categories")

    def form_valid(self, form):
        messages.success(self.request, "Cambios guardados.")
        return super().form_valid(form)


class CategoryDeleteView(PanelAccessMixin, DeleteView):
    model = Category
    template_name = "panel/confirm_delete.html"
    success_url = reverse_lazy("panel:categories")
    extra_context = {"kind": "categoría", "cancel_url": reverse_lazy("panel:categories")}

    def form_valid(self, form):
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(
                self.request,
                "Esta categoría tiene proyectos. Puedes desactivarla en vez de eliminarla.",
            )
            return HttpResponseRedirect(reverse("panel:categories"))
        messages.success(self.request, "Categoría eliminada.")
        return HttpResponseRedirect(self.get_success_url())
