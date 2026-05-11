from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from users.forms import (
    LoginForm,
    ProfileEditForm,
    RegisterForm,
    TeamFinderPasswordChangeForm,
)
from users.models import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect("projects:list")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Регистрация прошла успешно. Теперь войдите в аккаунт.")
            return redirect("users:login")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("projects:list")

    if request.method == "POST":
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Вы успешно вошли в аккаунт.")
            return redirect(request.GET.get("next") or "projects:list")
    else:
        form = LoginForm(request=request)
    return render(request, "users/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из аккаунта.")
    return redirect("projects:list")


def user_detail_view(request, pk):
    profile_user = get_object_or_404(
        User.objects.prefetch_related("owned_projects__participants"),
        pk=pk,
    )
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлён.")
            return redirect("users:detail", pk=request.user.pk)
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form, "user": request.user})


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = TeamFinderPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Пароль успешно изменён.")
            return redirect("users:detail", pk=request.user.pk)
    else:
        form = TeamFinderPasswordChangeForm(user=request.user)
    return render(request, "users/change_password.html", {"form": form})


def users_list_view(request):
    participants_qs = User.objects.all().order_by("-date_joined")
    active_filter = ""

    if request.user.is_authenticated:
        active_filter = request.GET.get("filter", "")
        if active_filter == "owners-of-favorite-projects":
            project_ids = request.user.favorites.values_list("id", flat=True)
            participants_qs = participants_qs.filter(owned_projects__id__in=project_ids)
        elif active_filter == "owners-of-participating-projects":
            participants_qs = participants_qs.filter(
                owned_projects__participants=request.user
            )
        elif active_filter == "interested-in-my-projects":
            my_project_ids = request.user.owned_projects.values_list("id", flat=True)
            participants_qs = participants_qs.filter(
                favorites__id__in=my_project_ids
            ).exclude(pk=request.user.pk)
        elif active_filter == "participants-of-my-projects":
            my_project_ids = request.user.owned_projects.values_list("id", flat=True)
            participants_qs = participants_qs.filter(
                participating_projects__id__in=my_project_ids
            ).exclude(pk=request.user.pk)

    participants_qs = participants_qs.distinct()
    paginator = Paginator(participants_qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {"participants": page_obj, "active_filter": active_filter}
    return render(request, "users/participants.html", context)
