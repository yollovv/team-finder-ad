from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from projects.forms import ProjectForm
from projects.models import Project


def project_list_view(request):
    projects = Project.objects.select_related("owner").prefetch_related("participants")
    paginator = Paginator(projects, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "projects/project_list.html", {"projects": page_obj})


def project_detail_view(request, pk):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        pk=pk,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def favorite_projects_view(request):
    projects = request.user.favorites.select_related("owner").prefetch_related("participants")
    paginator = Paginator(projects, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "projects/favorite_projects.html", {"projects": page_obj})


@login_required
def create_project_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, "Проект успешно опубликован.")
            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm()
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required
def edit_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id and not request.user.is_superuser:
        messages.error(request, "Вы не можете редактировать этот проект.")
        return redirect("projects:detail", pk=pk)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            messages.success(request, "Изменения проекта сохранены.")
            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True, "project": project},
    )


@require_POST
def toggle_favorite_view(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "auth_required", "login_url": "/users/login/"}, status=401)

    project = get_object_or_404(Project, pk=pk)
    if request.user.favorites.filter(pk=project.pk).exists():
        request.user.favorites.remove(project)
        is_favorite = False
    else:
        request.user.favorites.add(project)
        is_favorite = True
    return JsonResponse({"status": "ok", "favorite": is_favorite})


@login_required
@require_POST
def toggle_participate_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id == request.user.id:
        return JsonResponse({"status": "error", "detail": "owner_cannot_participate"}, status=400)
    if project.status == Project.Status.CLOSED:
        return JsonResponse({"status": "error", "detail": "project_closed"}, status=400)

    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True

    return JsonResponse({"status": "ok", "participant": participant})


@login_required
@require_POST
def complete_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id and not request.user.is_superuser:
        return JsonResponse({"status": "error", "detail": "forbidden"}, status=403)
    project.status = Project.Status.CLOSED
    project.save(update_fields=("status", "updated_at"))
    return JsonResponse({"status": "ok"})
