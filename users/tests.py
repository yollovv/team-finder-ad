from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from projects.models import Project
from users.models import User


HTTP_STATUS_OK = HTTPStatus.OK
FILTER_OWNERS_OF_FAVORITE_PROJECTS = "owners-of-favorite-projects"
FILTER_PARTICIPANTS_OF_MY_PROJECTS = "participants-of-my-projects"


class UserViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="pass12345",
            name="Ivan",
            surname="Ivanov",
        )
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="pass12345",
            name="Petr",
            surname="Petrov",
        )
        self.project = Project.objects.create(
            owner=self.owner,
            name="Owner project",
            description="Desc",
        )
        self.project.participants.add(self.user)
        self.user.favorites.add(self.project)

    def test_register_page_available(self):
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, HTTP_STATUS_OK)

    def test_login_with_email(self):
        response = self.client.post(
            reverse("users:login"),
            data={"email": "user@example.com", "password": "pass12345"},
            follow=True,
        )
        self.assertEqual(response.status_code, HTTP_STATUS_OK)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_user_detail_page_available(self):
        response = self.client.get(reverse("users:detail", args=(self.user.pk,)))
        self.assertEqual(response.status_code, HTTP_STATUS_OK)
        self.assertContains(response, "Ivan Ivanov")

    def test_users_filter_owners_of_favorite_projects(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("users:list"), {"filter": FILTER_OWNERS_OF_FAVORITE_PROJECTS})
        self.assertEqual(response.status_code, HTTP_STATUS_OK)
        participants = response.context["participants"]
        self.assertIn(self.owner, list(participants))

    def test_users_filter_participants_of_my_projects(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("users:list"), {"filter": FILTER_PARTICIPANTS_OF_MY_PROJECTS})
        self.assertEqual(response.status_code, HTTP_STATUS_OK)
        participants = response.context["participants"]
        self.assertIn(self.user, list(participants))
