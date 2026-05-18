from django.db import models


class Project(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Открыт"
        CLOSED = "closed", "Закрыт"

    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор",
    )
    name = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    github_url = models.URLField("GitHub URL", blank=True)
    status = models.CharField(
        "Статус",
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
    )
    participants = models.ManyToManyField(
        "users.User",
        related_name="participating_projects",
        blank=True,
        verbose_name="Участники",
    )
    created_at = models.DateTimeField("Дата публикации", auto_now_add=True)
    updated_at = models.DateTimeField("Изменено", auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.name

