from django.contrib.auth.models import AbstractUser
from django.db import models

from users.managers import UserManager


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None

    name = models.CharField("Имя", max_length=150)
    surname = models.CharField("Фамилия", max_length=150)
    email = models.EmailField("Email", unique=True)
    about = models.TextField("О себе", blank=True)
    phone = models.CharField("Телефон", max_length=32, blank=True)
    github_url = models.URLField("GitHub", blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="favorited_by",
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    class Meta:
        ordering = ("-date_joined",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.name} {self.surname}".strip() or self.email
