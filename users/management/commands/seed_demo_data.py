from django.core.management.base import BaseCommand

from projects.models import Project
from users.models import User


class Command(BaseCommand):
    help = "Создаёт демонстрационных пользователей и проекты."

    def handle(self, *args, **options):
        users_payload = [
            {
                "email": "alice@example.com",
                "name": "Alice",
                "surname": "Brown",
                "about": "Backend developer",
            },
            {
                "email": "bob@example.com",
                "name": "Bob",
                "surname": "Smith",
                "about": "UI/UX designer",
            },
            {
                "email": "carol@example.com",
                "name": "Carol",
                "surname": "White",
                "about": "Fullstack engineer",
            },
        ]

        created_users = []
        for payload in users_payload:
            user, created = User.objects.get_or_create(
                email=payload["email"],
                defaults={
                    "name": payload["name"],
                    "surname": payload["surname"],
                    "about": payload["about"],
                },
            )
            if created:
                user.set_password("password123")
                user.save(update_fields=("password",))
            created_users.append(user)

        projects_payload = [
            {
                "owner": created_users[0],
                "name": "Task tracker",
                "description": "Web app for tracking tasks in pet projects.",
            },
            {
                "owner": created_users[1],
                "name": "Design system kit",
                "description": "Reusable UI-kit for startup prototypes.",
            },
            {
                "owner": created_users[2],
                "name": "Study planner",
                "description": "Planner for students with reminders and analytics.",
            },
        ]

        created_projects = []
        for payload in projects_payload:
            project, _ = Project.objects.get_or_create(
                owner=payload["owner"],
                name=payload["name"],
                defaults={"description": payload["description"]},
            )
            created_projects.append(project)

        # Demo links between users/projects for variant 1 filters.
        created_projects[0].participants.add(created_users[1], created_users[2])
        created_projects[1].participants.add(created_users[0])
        created_users[0].favorites.add(created_projects[1])
        created_users[1].favorites.add(created_projects[0])
        created_users[2].favorites.add(created_projects[0], created_projects[1])

        self.stdout.write(self.style.SUCCESS("Демо-данные успешно созданы."))
