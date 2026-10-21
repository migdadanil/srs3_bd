from django.core.management.base import BaseCommand
from appeals.models import Category, Ticket
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Наполнение базы данных реалистичными заявками студентов МАИ"

    def handle(self, *args, **kwargs):
        user, _ = User.objects.get_or_create(
            username="student_mai", defaults={"email": "student@mai.ru"}
        )
        if not user.password:
            user.set_password("mai_secure_2026")
            user.save()

        categories_names = [
            "Академические вопросы",
            "Деканат и справки",
            "Общежитие и кампус",
            "Стипендии и матпомощь",
        ]

        cat_objs = {}
        for title in categories_names:
            c, _ = Category.objects.get_or_create(name=title)
            cat_objs[title] = c

        tickets_data = [
            ("Запрос академической справки за 3 семестр", "Деканат и справки", "new"),
            (
                "Перенос срока сдачи курсового проекта по СПОиБД",
                "Академические вопросы",
                "in_progress",
            ),
            (
                "Продление электронного пропуска в корпус 3",
                "Общежитие и кампус",
                "resolved",
            ),
            (
                "Заявление на повышенную академическую стипендию",
                "Стипендии и матпомощь",
                "in_progress",
            ),
            (
                "Согласование индивидуального плана практики",
                "Академические вопросы",
                "new",
            ),
            (
                "Замена временного пропуска в общежитие №5",
                "Общежитие и кампус",
                "resolved",
            ),
        ]

        created_count = 0
        for title, cat_name, status in tickets_data:
            if not Ticket.objects.filter(title=title).exists():
                Ticket.objects.create(
                    title=title,
                    description="Автоматически сформированное обращение студента кафедры 317.",
                    category=cat_objs[cat_name],
                    status=status,
                    owner=user,
                )
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Успешно создано заявок: {created_count}")
        )
