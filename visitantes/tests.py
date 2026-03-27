from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from usuarios.models import CustomUser

from .models import Visit, Visitor


class VisitorAPITests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='receptionist',
            email='reception@museum.com',
            password='testpass123',
            user_type='ADMIN',
        )
        self.client.force_authenticate(user=self.user)

        self.visitor = Visitor.objects.create(
            name='João Silva',
            document='12345678900',
            visitor_type='INDIVIDUAL',
            email='joao@email.com',
            phone='11999999999',
            created_by=self.user,
            updated_by=self.user,
        )

    def test_list_visitors(self):
        url = reverse('visitor-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_retrieve_visitor(self):
        url = reverse('visitor-detail', kwargs={'pk': self.visitor.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'João Silva')

    def test_create_visitor(self):
        url = reverse('visitor-list')
        data = {
            'name': 'Maria Souza',
            'document': '98765432100',
            'visitor_type': 'GROUP',
            'email': 'maria@email.com',
            'phone': '11888888888',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Visitor.objects.count(), 2)
        self.assertEqual(response.data['name'], 'Maria Souza')

    def test_update_visitor(self):
        url = reverse('visitor-detail', kwargs={'pk': self.visitor.pk})
        response = self.client.patch(url, {'phone': '11777777777'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.visitor.refresh_from_db()
        self.assertEqual(self.visitor.phone, '11777777777')

    def test_delete_visitor(self):
        url = reverse('visitor-detail', kwargs={'pk': self.visitor.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Visitor.objects.count(), 0)

    def test_search_visitor_by_name(self):
        url = f"{reverse('visitor-list')}?search=João"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_unauthenticated_user_cannot_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('visitor-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_total_visits_count(self):
        """Ensure total_visits is computed correctly."""
        url = reverse('visitor-detail', kwargs={'pk': self.visitor.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['total_visits'], 0)


class CheckInAPITests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='receptionist',
            email='reception@museum.com',
            password='testpass123',
            user_type='ADMIN',
        )
        self.client.force_authenticate(user=self.user)

        self.visitor = Visitor.objects.create(
            name='Carlos Lima',
            visitor_type='INDIVIDUAL',
            created_by=self.user,
            updated_by=self.user,
        )

    def test_check_in_with_new_visitor(self):
        """Check-in should create a new visitor and a visit record."""
        url = reverse('visit-check-in')
        data = {
            'name': 'Ana Paula',
            'visitor_type': 'INDIVIDUAL',
            'companion_count': 0,
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('ticket_code', response.data)
        self.assertIn('qr_code_base64', response.data)
        self.assertIsNotNone(response.data['qr_code_base64'])
        self.assertEqual(Visit.objects.count(), 1)
        self.assertEqual(Visitor.objects.count(), 2)

    def test_check_in_with_existing_visitor(self):
        """Check-in with visitor_id should reuse the existing visitor."""
        url = reverse('visit-check-in')
        data = {
            'visitor_id': self.visitor.pk,
            'companion_count': 2,
            'notes': 'Group visit',
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['visitor'], self.visitor.pk)
        self.assertEqual(Visit.objects.count(), 1)
        self.assertEqual(Visitor.objects.count(), 1)  # no new visitor created

    def test_check_in_missing_name_and_visitor_id(self):
        """Check-in without visitor identification should return 400."""
        url = reverse('visit-check-in')
        data = {'companion_count': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_in_with_nonexistent_visitor_id(self):
        """Check-in with a nonexistent visitor_id should return 404."""
        url = reverse('visit-check-in')
        data = {'visitor_id': 9999}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_qr_code_is_valid_base64(self):
        """QR code in the response must be a valid base64 string."""
        import base64

        url = reverse('visit-check-in')
        data = {'name': 'Teste QR', 'visitor_type': 'INDIVIDUAL'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        qr_base64 = response.data['qr_code_base64']
        try:
            decoded = base64.b64decode(qr_base64)
            self.assertTrue(len(decoded) > 0)
        except Exception:
            self.fail("qr_code_base64 is not valid base64")

    def test_unauthenticated_user_cannot_check_in(self):
        self.client.force_authenticate(user=None)
        url = reverse('visit-check-in')
        response = self.client.post(url, {'name': 'Test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CheckOutAPITests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='receptionist',
            email='reception@museum.com',
            password='testpass123',
            user_type='ADMIN',
        )
        self.client.force_authenticate(user=self.user)

        self.visitor = Visitor.objects.create(
            name='Pedro Costa',
            visitor_type='INDIVIDUAL',
            created_by=self.user,
            updated_by=self.user,
        )
        self.visit = Visit.objects.create(
            visitor=self.visitor,
            companion_count=0,
            registered_by=self.user,
        )

    def test_check_out_success(self):
        """Check-out should set check_out_at and return duration."""
        url = reverse('visit-check-out')
        data = {'ticket_code': str(self.visit.ticket_code)}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['check_out_at'])
        self.assertIsNotNone(response.data['duration_minutes'])
        self.assertFalse(response.data['is_active'])

        self.visit.refresh_from_db()
        self.assertIsNotNone(self.visit.check_out_at)

    def test_check_out_invalid_ticket(self):
        """Check-out with a nonexistent ticket should return 404."""
        url = reverse('visit-check-out')
        data = {'ticket_code': '00000000-0000-0000-0000-000000000000'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_check_out_already_checked_out(self):
        """Attempting check-out on a finished visit should return 400."""
        from django.utils import timezone

        self.visit.check_out_at = timezone.now()
        self.visit.save()

        url = reverse('visit-check-out')
        data = {'ticket_code': str(self.visit.ticket_code)}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_out_with_malformed_uuid(self):
        """Malformed ticket_code should return 400."""
        url = reverse('visit-check-out')
        data = {'ticket_code': 'not-a-valid-uuid'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_user_cannot_check_out(self):
        self.client.force_authenticate(user=None)
        url = reverse('visit-check-out')
        response = self.client.post(url, {'ticket_code': str(self.visit.ticket_code)})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class VisitListAPITests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='receptionist',
            email='reception@museum.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)

        self.visitor = Visitor.objects.create(
            name='Fernanda Rocha',
            visitor_type='SCHOOL',
            created_by=self.user,
            updated_by=self.user,
        )
        self.visit = Visit.objects.create(
            visitor=self.visitor,
            companion_count=25,
            registered_by=self.user,
        )

    def test_list_visits(self):
        url = reverse('visit-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_retrieve_visit(self):
        url = reverse('visit-detail', kwargs={'pk': self.visit.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['companion_count'], 25)
        self.assertTrue(response.data['is_active'])

    def test_visit_is_active_before_checkout(self):
        url = reverse('visit-detail', kwargs={'pk': self.visit.pk})
        response = self.client.get(url, format='json')
        self.assertTrue(response.data['is_active'])
        self.assertIsNone(response.data['duration_minutes'])