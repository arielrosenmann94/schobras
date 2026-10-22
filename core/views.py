from django.shortcuts import render

from projects.models import Project

FEATURED_LIMIT = 6


def home(request):
    """Inicio: una página larga con anclas y hasta 6 proyectos destacados."""
    featured = (
        Project.objects.published()
        .filter(is_featured=True)
        .select_related("category")
        .prefetch_related("photos")[:FEATURED_LIMIT]
    )
    return render(request, "core/home.html", {"featured_projects": featured})
