from django.test import TestCase
from django.urls import reverse

from projects.models import Project
from users.models import User


class ProjectViewsTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="pass12345",
            name="Owner",
            surname="User",
        )
        self.member = User.objects.create_user(
            email="member@example.com",
            password="pass12345",
            name="Member",
            surname="User",
        )
        self.project = Project.objects.create(
            owner=self.owner,
            name="Test project",
            description="Desc",
        )

    def test_projects_list_is_available(self):
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test project")

    def test_toggle_favorite_requires_auth(self):
        response = self.client.post(reverse("projects:toggle-favorite", args=(self.project.pk,)))
        self.assertEqual(response.status_code, 401)

    def test_toggle_favorite_for_authorized_user(self):
        self.client.force_login(self.member)
        response = self.client.post(reverse("projects:toggle-favorite", args=(self.project.pk,)))
        self.assertEqual(response.status_code, 200)
        self.member.refresh_from_db()
        self.assertTrue(self.member.favorites.filter(pk=self.project.pk).exists())

    def test_project_detail_shows_favorite_toggle_for_authenticated_user(self):
        self.client.force_login(self.member)
        response = self.client.get(reverse("projects:detail", args=(self.project.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "project-fav-icon")

    def test_toggle_participate(self):
        self.client.force_login(self.member)
        response = self.client.post(reverse("projects:toggle-participate", args=(self.project.pk,)))
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertTrue(self.project.participants.filter(pk=self.member.pk).exists())

    def test_owner_can_complete_project(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("projects:complete", args=(self.project.pk,)))
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.Status.CLOSED)
