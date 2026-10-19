from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=150, unique=True, verbose_name="Категория обращения"
    )
    code = models.CharField(max_length=50, blank=True, verbose_name="Код подразделения")

    class Meta:
        verbose_name = "Категория обращения"
        verbose_name_plural = "Категории обращений"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Ticket(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        PROGRESS = "progress", "В работе"
        DONE = "done", "Выполнена"

    class Priority(models.TextChoices):
        LOW = "low", "Низкий"
        MEDIUM = "medium", "Обычный"
        HIGH = "high", "Срочный"

    title = models.CharField(max_length=200, verbose_name="Тема обращения")
    description = models.TextField(blank=True, verbose_name="Подробное описание")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="tickets",
        verbose_name="Категория",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets",
        verbose_name="Студент",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NEW, verbose_name="Статус"
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name="Приоритет",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подачи")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Обращение студента"
        verbose_name_plural = "Обращения студентов"
        ordering = ["-created_at"]

    def __str__(self):
        return f"№{self.id} — {self.title}"
