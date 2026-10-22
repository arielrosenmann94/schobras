import logging

from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.models import SiteSettings
from projects import services
from projects.models import Category, Project, ProjectPhoto

from .forms import (
    CategoryForm,
    PanelAuthenticationForm,
    PhotoUploadForm,
    ProjectForm,
    SiteSettingsForm,
)
from .permissions import AdminRequiredMixin, PanelAccessMixin

try:
    from cloudinary.exceptions import Error as CloudinaryError
except ImportError:  # cloudinary solo es obligatorio en producción
    CloudinaryError = OSError

logger = logging.getLogger(__name__)

# Fallas del almacenamiento de fotos (disco local o Cloudinary).
STORAGE_ERRORS = (CloudinaryError, OSError)
UPLOAD_ERROR = "No se pudo subir la foto. Inténtalo de nuevo en unos minutos."


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
        services.delete_project(self.object)
        messages.success(self.request, "Proyecto eliminado.")
        return HttpResponseRedirect(self.get_success_url())


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


class ProjectPhotosView(PanelAccessMixin, View):
    template_name = "panel/photos.html"

    def render_page(self, request, project, form):
        photos = project.photos.all()
        return render(request, self.template_name, {"project": project, "photos": photos, "form": form})

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        return self.render_page(request, project, PhotoUploadForm())

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = PhotoUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return self.render_page(request, project, form)
        try:
            created = services.add_photos(project, form.cleaned_data["images"])
        except STORAGE_ERRORS:
            # Límite HTTP: se registra el detalle y la editora ve un mensaje claro.
            logger.exception("No se pudieron guardar las fotos del proyecto %s", project.pk)
            form.add_error("images", UPLOAD_ERROR)
            return self.render_page(request, project, form)
        if len(created) == 1:
            messages.success(request, "Foto subida.")
        else:
            messages.success(request, f"{len(created)} fotos subidas.")
        return redirect("panel:project_photos", pk=project.pk)


class PhotoActionView(PanelAccessMixin, View):
    http_method_names = ["post"]
    action = None
    message = ""

    def post(self, request, pk):
        photo = get_object_or_404(ProjectPhoto, pk=pk)
        project_pk = photo.project_id
        self.apply(photo)
        messages.success(request, self.message)
        return redirect("panel:project_photos", pk=project_pk)

    def apply(self, photo):
        raise NotImplementedError


class PhotoUpView(PhotoActionView):
    message = "Foto movida hacia arriba."

    def apply(self, photo):
        services.move_photo(photo, "up")


class PhotoDownView(PhotoActionView):
    message = "Foto movida hacia abajo."

    def apply(self, photo):
        services.move_photo(photo, "down")


class PhotoCoverView(PhotoActionView):
    message = "Esa foto ahora es la portada."

    def apply(self, photo):
        services.set_cover(photo)


class PhotoDeleteView(PhotoActionView):
    message = "Foto eliminada."

    def apply(self, photo):
        services.delete_photo(photo)


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


class SiteSettingsView(AdminRequiredMixin, UpdateView):
    form_class = SiteSettingsForm
    template_name = "panel/settings.html"
    success_url = reverse_lazy("panel:settings")

    def get_object(self, queryset=None):
        return SiteSettings.load()

    def form_valid(self, form):
        messages.success(self.request, "Configuración guardada.")
        return super().form_valid(form)
