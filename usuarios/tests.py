from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser

class UserAPITests(APITestCase):
    def setUp(self):
        """
        Set up two types of users for permission testing: an admin and a regular user.
        """
        self.admin_user = CustomUser.objects.create_superuser(
            username='admin', email='admin@example.com', password='password123'
        )
        self.regular_user = CustomUser.objects.create_user(
            username='seller', email='seller@example.com', password='password123',
            user_type='VENDEDOR'
        )

    # --- Tests performed as an ADMIN user ---
    def test_admin_can_list_users(self):
        """
        Ensure an admin can list all users.
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_admin_can_retrieve_other_user(self):
        """
        Ensure an admin can retrieve the details of another user.
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user-detail', kwargs={'pk': self.regular_user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.regular_user.username)

    def test_admin_can_create_user(self):
        """
        Ensure an admin can create a new user.
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('user-list')
        data = {"username": "newuser", "email": "new@user.com", "password": "password123", "user_type": "STOCKCLERK"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 3)


    # --- Tests performed as a REGULAR user ---
    def test_regular_user_cannot_list_users(self):
        """
        Ensure a non-admin user is forbidden from listing all users.
        """
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_can_retrieve_self(self):
        """
        Ensure a regular user can retrieve their own profile details.
        """
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('user-detail', kwargs={'pk': self.regular_user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.regular_user.username)

    def test_regular_user_cannot_retrieve_other(self):
        """
        Ensure a regular user is forbidden from retrieving another user's profile.
        """
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('user-detail', kwargs={'pk': self.admin_user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_can_update_self(self):
        """
        Ensure a regular user can update their own profile.
        """
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('user-detail', kwargs={'pk': self.regular_user.pk})
        data = {"first_name": "Updated Name"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.first_name, "Updated Name")

    def test_regular_user_cannot_create_user(self):
        """
        Ensure a regular user is forbidden from creating users.
        """
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('user-list')
        data = {"username": "anotheruser", "email": "another@user.com", "password": "password123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Test performed as an UNAUTHENTICATED user ---
    def test_unauthenticated_user_cannot_access(self):
        """
        Ensure unauthenticated users receive a 401 Unauthorized error.
        """
        self.client.force_authenticate(user=None)
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)