from django.contrib.auth.views import LoginView
from django.views.generic import ListView

from projects.models import Project

from .forms import PanelAuthenticationForm
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
