from django.urls import path

from users import views

app_name = "users"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("list", views.users_list_view),
    path("list/", views.users_list_view, name="list"),
    path("edit-profile/", views.edit_profile_view, name="edit-profile"),
    path("edit-profile", views.edit_profile_view),
    path("change-password/", views.change_password_view, name="change-password"),
    path("<int:pk>/", views.user_detail_view, name="detail"),
    path("<int:pk>", views.user_detail_view),
]
