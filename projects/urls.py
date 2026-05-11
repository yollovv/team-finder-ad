from django.urls import path

from projects import views

app_name = "projects"

urlpatterns = [
    path("", views.project_list_view),
    path("list", views.project_list_view),
    path("list/", views.project_list_view, name="list"),
    path("create-project", views.create_project_view),
    path("create-project/", views.create_project_view, name="create"),
    path("favorites", views.favorite_projects_view),
    path("favorites/", views.favorite_projects_view, name="favorites"),
    path("<int:pk>/", views.project_detail_view, name="detail"),
    path("<int:pk>", views.project_detail_view),
    path("<int:pk>/edit/", views.edit_project_view, name="edit"),
    path("<int:pk>/edit", views.edit_project_view),
    path("<int:pk>/toggle-favorite/", views.toggle_favorite_view, name="toggle-favorite"),
    path("<int:pk>/toggle-participate/", views.toggle_participate_view, name="toggle-participate"),
    path("<int:pk>/complete/", views.complete_project_view, name="complete"),
]
